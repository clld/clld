# coding: utf8
"""Functionality to create a full RDF dump and register a dataset with datahub.io."""
from __future__ import division, absolute_import, print_function, unicode_literals
import os
from tempfile import mkdtemp
import json
from subprocess import check_call

from six import BytesIO, binary_type
import requests
from rdflib import Graph
from sqlalchemy.exc import InvalidRequestError
from clldutils.path import Path, as_posix
from clldutils import jsonlib

from clld.lib import rdf
from clld.db.util import page_query
from clld.db.meta import DBSession
from clld.db.models.common import Dataset
from clld.web.adapters.rdf import Rdf
from clld import RESOURCES


def datahub(action, **params):  # pragma: no cover
    """Access datahub.io's API.

    :param action: Name of the action to perform.
    :param params: Payload.
    :return: result member of the JSON response in case of success else None.
    """
    res = requests.post(
        "http://datahub.io/api/action/" + action,
        data=json.dumps(params),
        headers={
            'authorization': os.environ.get('DATAHUB_API_KEY'),
            'content-type': 'application/json'})
    res = res.json()
    if res['success']:
        return res['result']


def n3(graph, with_head=False):  # pragma: no cover
    """Serialize an RDF graph as N3, by default ommitting the namespace declarations."""
    out = BytesIO()
    graph.serialize(out, format='n3')
    out.seek(0)
    res = out.read()
    if with_head:
        return res
    return res.split(binary_type('\n\n'), 1)[1]


def get_graph(obj, req, rscname):  # pragma: no cover
    adapter = Rdf(obj)
    adapter.template = rscname + '/rdf.mako'
    return adapter.render(obj, req)


def llod_func(args):  # pragma: no cover
    """Create an RDF dump and compute some statistics about it."""
    tmp = Path(mkdtemp())
    count_rsc = 0
    count_triples = 0

    tmp_dump = tmp.joinpath('rdf.n3')
    with open(as_posix(tmp_dump), 'w') as fp:
        for rsc in RESOURCES:
            args.log.info('Resource type %s ...' % rsc.name)
            try:
                q = DBSession.query(rsc.model)
            except InvalidRequestError:
                args.log.info('... skipping')
                continue
            for obj in page_query(q.order_by(rsc.model.pk), n=10000, verbose=True):
                graph = get_graph(obj, args.env['request'], rsc.name)
                count_triples += len(graph)
                count_rsc += 1
                fp.write(n3(graph, with_head=count_rsc == 1))
            args.log.info('... finished')

    # put in args.data_file('..', 'static', 'download')?
    md = {'path': as_posix(tmp), 'resources': count_rsc, 'triples': count_triples}
    md.update(count_links(as_posix(tmp_dump)))
    jsonlib.dump(md, args.data_file('rdf-metadata.json'))
    print(md)

    dataset = Dataset.first()
    rdf_dump = args.module_dir.joinpath(
        'static', 'download', '%s-dataset.n3' % dataset.id)
    tmp_dump.copy(rdf_dump)
    check_call('gzip -f %s' % rdf_dump, shell=True)
    print(str(rdf_dump))


def register(args):  # pragma: no cover
    """Register a dataset with datahub.io."""
    dataset = Dataset.first()
    name = 'clld-' + dataset.id.lower()
    package = datahub('package_show', id=name)
    if not package:
        package = datahub(
            'package_create',
            **{'name': name, 'title': 'CLLD-' + dataset.id.upper(), 'owner_org': 'clld'})
    md = {
        'url': 'http://%s' % dataset.domain,
        'notes': '%s published by the CLLD project' % dataset.name,
        'maintainer': 'CLLD Project',
        'tags': [
            {'name': 'linguistics'},
            {'name': 'lod'},
            {'name': 'llod'},
        ]}
    if dataset.contact:
        md['maintainer_email'] = dataset.contact
    if dataset.license:
        if 'creativecommons.org/licenses/by/' in dataset.license:
            md['license_id'] = 'cc-by-sa'
            md['license_title'] = "Creative Commons Attribution Share-Alike"
        elif 'creativecommons.org/' in dataset.license and '-nc' in dataset.license:
            md['license_id'] = 'cc-nc'
            md['license_title'] = "Creative Commons Non-Commercial (Any)"
    rdf_md = args.data_file('rdf-metadata.json')
    if rdf_md.exists():
        rdf_md = jsonlib.load(rdf_md)
        md['extras'] = [
            {'key': k, 'value': str(rdf_md[k])} for k in rdf_md.keys()
            if k.split(':')[0] in ['triples', 'resources', 'links']]

    package = datahub('package_update', id=name, **md)
    resources = [rsc['name'] for rsc in package['resources']]
    if 'VoID description' not in resources:
        rsc = datahub(
            'resource_create',
            package_id=package['id'],
            name='VoID description',
            url='http://%s/void.ttl' % dataset.domain,
            format='meta/void',
            mimetype='text/turtle')
        assert rsc

    rdf_dump = '%s-dataset.n3.gz' % dataset.id
    if ('RDF dump' not in resources) \
            and args.module_dir.joinpath('static', 'download', rdf_dump).exists():
        rsc = datahub(
            'resource_create',
            package_id=package['id'],
            name='RDF dump',
            url='http://%s/static/download/%s' % (dataset.domain, rdf_dump),
            format='text/n3',
            mimetype='text/n3')
        assert rsc

    print('>>> Make sure to upload the RDF dump to the production site.')


def count_links(p):  # pragma: no cover
    g = Graph()
    g.parse(p, format='n3')
    res = {
        'links:lexvo': len(list(g.triples(
            (None, rdf.NAMESPACES['lexvo']['iso639P3PCode'], None)))),
    }

    for dataset, predicate, domain in [
        ('dbpedia', 'owl:sameAs', "http://dbpedia.org"),
        ('geonames', 'dcterms:spatial', "http://www.geonames.org"),
        ('gold', 'rdf:type', "http://purl.org/linguistics/gold/"),
        ('clld-wals', 'skos:broader', "http://wals.info/"),
        ('clld-glottolog', 'owl:sameAs', "http://glottolog.org/")
    ]:
        q = g.query('SELECT ?s ?o WHERE {?s %s ?o. FILTER(STRSTARTS(STR(?o), "%s")).}' % (
            predicate, domain))
        count = len(list(q))
        if count:
            res['links:' + dataset] = count
    return res
