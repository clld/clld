"""
Complete archiving workflow.

1. run ``freeze_func`` to create a database dump as zip archive of csv files
2. commit and push the dump to the repos
3. run ``create_release_func`` to create a release of the repos (thereby triggering the
   zenodo hook)
4. lookup DOI created by zenodo
5. run ``update_zenodo_metadata_func`` to update the associated metadata at ZENODO.

``unfreeze_func`` can be used to recreate an app's database from a frozen set of csv
files.
"""
from __future__ import unicode_literals, division, absolute_import, print_function
import os
from zipfile import ZipFile, ZIP_DEFLATED
import json
from tempfile import mkdtemp
from datetime import datetime, date
import importlib

from dateutil.parser import parse
from sqlalchemy import Boolean
from sqlalchemy.sql import select
import requests
try:
    import github3
except ImportError:
    github3 = None
from clldutils import jsonlib
from clldutils.path import Path, as_posix, rmtree
from clldutils.dsv import reader, UnicodeWriter

from clld.web.adapters.md import TxtCitation
from clld.web.adapters.csv import CsvmJsonAdapter
from clld.scripts.util import parsed_args
from clld.db.meta import Base, DBSession, JSONEncodedDict
from clld.db.util import set_alembic_version, get_alembic_version
from clld.util import DeclEnumType


def create_release_func(args, tag=None, name=None, dataset=None):  # pragma: no cover
    """
    Create a release of a GitHub repository.

    .. seealso:: https://developer.github.com/v3/repos/releases/#create-a-release
    """
    if github3 is None:
        args.log.critical("github3 is not installed. Can't access the GitHub API.")
        return

    token = os.environ.get('GITHUB_TOKEN')
    if token is None:
        args.log.critical('Environment variable GITHUB_TOKEN must be set.')
        return

    req = args.env['request']
    dataset = dataset or req.dataset
    today = date.today()
    tag = tag or 'v%s-%s' % (today.year, today.month)

    repo = github3.login(token=token).repository('clld', args.module.__name__)
    return repo.create_release(
        tag,
        name='%s %s' % (name or dataset.name, tag[1:] if tag.startswith('v') else tag),
        body='<p>%s</p>' % TxtCitation(None).render(dataset, req).encode('utf8'))


def update_zenodo_metadata(**kw):  # pragma: no cover
    update_zenodo_metadata_func(parsed_args((('doi',), {}), bootstrap=True))


def update_zenodo_metadata_func(args, doi=None, dataset=None):  # pragma: no cover
    """
    Update the metadata registered by ZENODO for the dataset.

    This is necessary, because ZENODO derives the metadata upon upload from the GitHub
    repository. Thus, all and only committers end up as authors, etc.

    .. seealso:: https://zenodo.org/dev
    """
    from pprint import pprint
    dataset = dataset or args.env['request'].dataset
    doi = doi or args.doi
    token = os.environ.get('ZENODO_ACCESS_TOKEN')
    if not token:
        args.log.critical('Environment variable ZENODO_ACCESS_TOKEN must be set.')
        return

    def api(path='', method='GET', **kw):
        verb = method.upper()
        method = getattr(requests, method.lower())
        res = method(
            "https://zenodo.org/api/deposit/depositions%s?access_token=%s" % (
                path, token),
            **kw)
        print(verb, '/api/deposit/depositions' + path, res.status_code)
        return res

    zid = None
    md = {}
    for deposition in api().json():
        if deposition['doi'] == doi:
            zid = deposition['id']
            md = deposition['metadata']
            break

    if not zid:
        return

    if 'clld' not in [c['identifier'] for c in md['communities']]:
        md['communities'].append({
            "identifier": "clld",
            "provisional": True,
            "title": "Cross-Linguistic Linked Data"})

    md['creators'] = []
    for editor in dataset.editors:
        md['creators'].append(dict(
            name=editor.contributor.name,
            affiliation=editor.contributor.description or ''))

    md['imprint_place'] = dataset.publisher_place or ''
    md['imprint_publisher'] = dataset.publisher_name or ''
    md["keywords"].append("linguistics")
    md["keywords"] = list(set(md['keywords']))
    if 'creativecommons.org' in dataset.license and '/by/' in dataset.license:
        md["license"] = "cc-by"
    md["notes"] = "This deposit contains both, the data of %s as well as the software "\
        "serving http://%s" % (dataset.name, dataset.domain)
    md["publication_date"] = dataset.published.isoformat()
    url = 'http://' + dataset.domain
    for ri in md["related_identifiers"]:
        if ri['identifier'] == url:
            break
    else:
        md["related_identifiers"].append(dict(
            identifier=url, relation='isSupplementTo', scheme='url'))
    md["upload_type"] = "dataset"

    res = api('/%s/actions/edit' % zid, method='post')
    assert res.status_code == 201

    headers = {"Content-Type": "application/json"}
    res = api(
        '/%s' % zid,
        method='put',
        data=json.dumps(dict(metadata={k: v for k, v in md.items() if v is not None})),
        headers=headers)
    if res.status_code == 200:
        res = api('/%s/actions/publish' % zid, method='post')
        assert res.status_code == 202
    else:
        pprint(res.json())
        pprint(md)
        api('/%s/actions/discard' % zid, method='post')


FREEZE_README = """
{0} data dump
{1}

Data of {0} is published under the following license:
{2}

It should be cited as

{3}

This package contains files in csv format [1] with corresponding schema
descriptions according to [2], representing rows in database tables of
the {0} web application [3,4].

[1] http://www.w3.org/TR/tabular-data-model/#syntax
[2] http://www.w3.org/TR/tabular-metadata/
[3] http://{4}
[4] https://github.com/clld/{5}
"""


def freeze_readme(dataset, req):  # pragma: no cover
    return FREEZE_README.format(
        dataset.name,
        '=' * (len(dataset.name.encode('utf8')) + len(' data dump')),
        dataset.license,
        TxtCitation(None).render(dataset, req),
        dataset.domain,
        dataset.id)


def _freeze(table, fpath):
    def conv(v, col):
        if v is None:
            return ''
        if isinstance(col.type, DeclEnumType):  # pragma: no cover
            return v.value
        if isinstance(col.type, JSONEncodedDict):
            return json.dumps(v)
        if isinstance(v, (datetime, date)):
            return v.isoformat()
        return v

    keys = [col.name for col in table.columns]
    cols = {col.name: col for col in table.columns}
    rows = [keys]

    for row in DBSession.execute(select([table])):
        rows.append([conv(row[key], cols[key]) for key in keys])

    if len(rows) > 1:
        with UnicodeWriter(fpath) as writer:
            writer.writerows(rows)


def freeze_func(args, dataset=None, with_history=True):
    dataset = dataset or args.env['request'].dataset
    dump_dir = args.data_file('dumps')
    if not dump_dir.exists():
        dump_dir.mkdir()
    dump_dir = dump_dir.resolve()

    with dump_dir.joinpath('README.txt').open('w', encoding='utf8') as fp:
        fp.write(freeze_readme(dataset, args.env['request']))

    db_version = get_alembic_version(DBSession)

    for table in Base.metadata.sorted_tables:
        csv = dump_dir.joinpath('%s.csv' % table.name)
        if with_history or not table.name.endswith('_history'):
            _freeze(table, csv)

        if csv.exists():
            csvm = '%s.%s' % (table.name, CsvmJsonAdapter.extension)
            doc = CsvmJsonAdapter.csvm_doc(
                csvm, args.env['request'], [(col.name, col) for col in table.columns])
            if db_version:
                # We (ab)use a dc:identifier property to pass the alembic revision of the
                # database to the unfreeze script.
                doc["dc:identifier"] = db_version  # pragma: no cover
            jsonlib.dump(doc, dump_dir.joinpath(csvm))

    with ZipFile(
            as_posix(args.data_file('..', 'data.zip')), 'w', ZIP_DEFLATED) as zipfile:
        for f in dump_dir.iterdir():
            if f.is_file():
                with f.open('rb') as fp:
                    zipfile.writestr(f.name, fp.read())


TYPE_MAP = {
    'http://www.w3.org/2001/XMLSchema#int': int,
    'http://www.w3.org/2001/XMLSchema#float': float,
    'http://www.w3.org/2001/XMLSchema#boolean': bool,
    'http://www.w3.org/2001/XMLSchema#dateTime': parse,
    'http://www.w3.org/2001/XMLSchema#date': lambda d: parse(d).date(),
}


def get_converter(schema, table):
    conv = {}
    default = lambda s: s
    for field in schema['columns']:
        conv[field['name']] = TYPE_MAP.get(field['datatype']['@id'], default)
    for col in table.columns:
        if isinstance(col.type, DeclEnumType):
            conv[col.name] = col.type.enum.from_string
        elif isinstance(col.type, Boolean):
            conv[col.name] = lambda v: v == 'True'
        elif isinstance(col.type, JSONEncodedDict):
            conv[col.name] = json.loads
    return conv


def converted(d, converter):
    for k in list(d.keys()):
        if k in converter:
            if d[k] != '':
                d[k] = converter[k](d[k])
            else:
                d[k] = None
    return d


def load(table, csv, engine):
    schema = jsonlib.load(csv.parent.joinpath(csv.stem + '.' + CsvmJsonAdapter.extension))
    converter = get_converter(schema['tableSchema'], table)
    engine.execute(
        table.insert(), [converted(d, converter) for d in reader(csv, dicts=True)])
    return schema.get("dc:identifier")


def unfreeze_func(args, engine=None):
    try:
        importlib.import_module(args.module.__name__)
    except ImportError:
        pass  # pragma: no cover
    engine = engine or DBSession.get_bind()
    data_dir = Path(mkdtemp())

    with ZipFile(as_posix(args.module_dir.joinpath('..', 'data.zip'))) as fp:
        fp.extractall(as_posix(data_dir))

    db_version = None
    for table in Base.metadata.sorted_tables:
        csv = data_dir.joinpath('%s.csv' % table.name)
        if csv.exists():
            db_version = load(table, csv, engine)

    if db_version:
        set_alembic_version(engine, db_version)  # pragma: no cover

    rmtree(data_dir)
