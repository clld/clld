# coding: utf8
from __future__ import division, absolute_import, print_function, unicode_literals
import os
from tempfile import mkdtemp
import json

from path import path
from six import BytesIO, binary_type
import requests

from clld.util import jsonload, jsondump
from clld.db.meta import DBSession
from clld.db.models.common import Dataset, Combination
from clld.scripts.util import parsed_args
from clld.web.adapters.rdf import Rdf
from clld import RESOURCES


def datahub(action, **params):  # pragma: no cover
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
    out = BytesIO()
    graph.serialize(out, format='n3')
    out.seek(0)
    res = out.read()
    if with_head:
        return res
    return res.split(binary_type('\n\n'))[1]


def get_graph(obj, req, rscname):  # pragma: no cover
    adapter = Rdf(obj)
    adapter.template = rscname + '/rdf.mako'
    return adapter.render(obj, req)


def llod(**kw):  # pragma: no cover
    llod_func(parsed_args(bootstrap=True))


def llod_func(args):  # pragma: no cover
    tmp = path(mkdtemp())
    count_rsc = 0
    count_triples = 0

    with open(tmp.joinpath('rdf.n3'), 'w') as fp:
        for rsc in RESOURCES:
            args.log.info('Resource type %s ...' % rsc.name)
            if rsc.model == Combination:
                continue
            for obj in DBSession.query(rsc.model).order_by(rsc.model.pk):
                graph = get_graph(obj, args.env['request'], rsc.name)
                count_triples += len(graph)
                count_rsc += 1
                fp.write(n3(graph, with_head=count_rsc == 1))
            args.log.info('... finished')

    #
    # TODO: put summary in json file (or in db?)
    # URL of dump, number of resources and number of triples.
    # put in args.data_file('..', 'static', 'download')?

    jsondump(
        {'path': tmp, 'resources': count_rsc, 'triples': count_triples},
        args.data_file('rdf-metadata.json'))

    print(tmp)
    print(count_rsc)
    print(count_triples)


def register(args):  # pragma: no cover
    dataset = Dataset.first()
    name = 'clld-' + dataset.id.lower()
    package = datahub('package_show', id=name)
    if not package:
        package = datahub(
            'package_create',
            **{'name': name, 'title': 'CLLD-' + dataset.id, 'owner_org': 'clld'})
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
        rdf_md = jsonload(rdf_md)
        md['extras'] = [
            {'key': k, 'value': str(rdf_md[k])} for k in ['triples', 'resources']]

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
