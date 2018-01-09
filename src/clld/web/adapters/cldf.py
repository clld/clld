from __future__ import unicode_literals
from collections import OrderedDict
import shutil

from sqlalchemy.orm import joinedload_all, joinedload
from pycldf import dataset
from pycldf import sources
from clldutils.path import TemporaryDirectory
from csvw.metadata import URITemplate, Column

from clld.web.adapters.download import Download
from clld.db.meta import DBSession
from clld.db.models.common import (
    ValueSet, Value, Parameter, Language, Contribution, Source, Sentence,
)
from clld.web.util.helpers import text_citation, get_url_template


def url_template(req, route, id_name):
    return URITemplate(get_url_template(
        req, route, relative=False, variable_map={'id': id_name}))


def source2source(req, source):
    """Harmonize the different Source implementations in clld and pycldf."""
    bibrecord = source.bibtex()
    fields = OrderedDict({'%s_url' % req.dataset.id: req.resource_url(source)})
    for key, value in bibrecord.items():
        fields[key] = '; '.join(value) if isinstance(value, list) else value
    return sources.Source(
        getattr(bibrecord.genre, 'value', bibrecord.genre) if bibrecord.genre else 'misc',
        source.id,
        **fields)


def iterrefs(obj):
    def _desc(d):
        return '[%s]' % d.replace(';', '.').replace('[', '{').replace(']', '}') \
            if d else ''

    # For backwards compatibility:
    if not hasattr(obj, 'references') and hasattr(obj, 'valueset'):
        obj = obj.valueset

    for r in obj.references:
        if r.source_pk:
            yield r.source_pk, _desc(r.description)


class CldfDownload(Download):
    ext = 'cldf'
    description = "Dataset in CLDF"

    def create(self, req, filename=None, verbose=True, outfile=None):
        with TemporaryDirectory() as tmpd:
            # what CLDF module are we dealing with?
            cldf_module = req.registry.settings.get('cldf_module', 'Wordlist')
            cls = getattr(dataset, cldf_module)
            ds = cls.in_dir(tmpd)
            ds.properties['dc:bibliographicCitation '] = text_citation(req, req.dataset)
            ds.properties['dc:publisher'] = '%s, %s' % (
                req.dataset.publisher_name, req.dataset.publisher_place)
            ds.properties['dc:license'] = req.dataset.license
            ds.properties['dc:issued'] = req.dataset.published.isoformat()
            ds.properties['dc:title'] = req.dataset.name
            ds.properties['dc:creator'] = req.dataset.formatted_editors()
            ds.properties['dc:identifier'] = req.resource_url(req.dataset)
            ds.properties['dcat:accessURL'] = req.route_url('download')
            ds.properties['dc:hasPart'] = []
            contribs = {}
            for contrib in DBSession.query(Contribution):
                contribs[contrib.pk] = contrib.id
                ds.properties['dc:hasPart'].append(req.resource_url(contrib))

            ds.add_component('ExampleTable')
            ds.add_component('ParameterTable')
            ds.add_component('LanguageTable')
            ds[ds.primary_table].tableSchema.columns.append(Column.fromvalue(
                {
                    'name': 'contribution',
                    'datatype': 'string',
                    'valueUrl': url_template(req, 'contribution', 'contribution').uri,
                }))

            ds['LanguageTable'].aboutUrl = url_template(req, 'language', 'ID')
            ds['ParameterTable'].aboutUrl = url_template(req, 'parameter', 'ID')
            ds[ds.primary_table].aboutUrl = url_template(req, 'value', 'ID')

            sources = {}
            for src in DBSession.query(Source):
                sources[src.pk] = src.id
                ds.sources.add(source2source(req, src))
            ds.write()
            params = OrderedDict()
            for o in DBSession.query(Parameter):
                params[o.pk] = {
                    'ID': o.id,
                    'name': o.name,
                }
            langs = OrderedDict()
            for o in DBSession.query(Language):
                langs[o.pk] = {
                    'ID': o.id,
                    'name': o.name,
                    'glottocode': o.glottocode}

            ds['ParameterTable'].write(params.values())
            ds['LanguageTable'].write(langs.values())
            ds['ExampleTable'].write([
                {
                    'ID': o.id,
                    'Language_ID': langs[o.language_pk]['ID'],
                    'Primary_Text': o.name,
                    'Analyzed_Word': o.analyzed.split('\t') if o.analyzed else [],
                    'Gloss': o.gloss.split('\t') if o.gloss else [],
                    'Translated_Text': o.description} for o in DBSession.query(Sentence)])

            values = []
            for v in DBSession.query(Value).join(Value.valueset).options(
                    joinedload_all(Value.valueset, ValueSet.references),
                    joinedload(Value.domainelement)):
                values.append({
                    'ID': v.id,
                    'Language_ID': langs[v.valueset.language_pk]['ID'],
                    'Parameter_ID': params[v.valueset.parameter_pk]['ID'],
                    'Value': (v.domainelement.name if v.domainelement else v.name) or '-',
                    'Form': 'spam',
                    'Source': [
                        '{0}{1}'.format(sources[spk], d) for spk, d in iterrefs(v)],
                    'contribution': contribs[v.valueset.contribution_pk],
                })
            ds[ds.primary_table].write(values)
            ds.validate()

            fname = outfile or self.abspath(req)
            shutil.make_archive(
                fname.parent.joinpath(fname.stem).as_posix(), 'zip', tmpd.as_posix())
