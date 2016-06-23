from __future__ import unicode_literals

from sqlalchemy.orm import joinedload_all, joinedload
from pycldf.dataset import Dataset
from pycldf.util import Archive
from pycldf.sources import Source

from clld.util import safe_overwrite
from clld.interfaces import ICldfDataset
from clld.web.adapters.download import Download, format_readme
from clld.db.meta import DBSession
from clld.db.models.common import (
    Contribution, ContributionContributor, ValueSet, Value, ValueSetReference,
)
from clld.web.util.helpers import text_citation, get_url_template


class CldfDataset(object):
    def __init__(self, obj):
        self.obj = obj

    def write(self, req, archive):
        ds = self.dataset(req)
        ds.write(archive=archive)

    def columns(self, req):
        return [
            'ID',
            {
                'name': 'Language_ID',
                'valueUrl': get_url_template(
                    req, 'language', variable_map={'id': 'Language_ID'})},
            'Language_name',
            {
                'name': 'Parameter_ID',
                'valueUrl': get_url_template(
                    req, 'parameter', variable_map={'id': 'Parameter_ID'})},
            'Parameter_name',
            'Value',
            'Source',
            'Comment',
        ]

    def row(self, req, value, refs):
        return [
            value.id,
            value.valueset.language.id,
            value.valueset.language.name,
            value.valueset.parameter.id,
            value.valueset.parameter.name,
            '%s' % value,
            refs,
            value.valueset.source or '',
        ]

    def refs_and_sources(self, req, obj):
        def _desc(d):
            return '[%s]' % d.replace(';', '.').replace('[', '{').replace(']', '}') \
                if d else ''

        sources = []
        refs = []
        for r in obj.references:
            if r.source:
                bibrecord = r.source.bibtex()
                refs.append('%s%s' % (r.source.id, _desc(r.description)))
                bibrecord['%s_url' % req.dataset.id] = req.resource_url(r.source)
                sources.append(Source(
                    getattr(bibrecord.genre, 'value', bibrecord.genre)
                    if bibrecord.genre else 'misc',
                    r.source.id,
                    **bibrecord))
        return ';'.join(refs), sources

    def value_query(self):
        return DBSession.query(Value)\
            .join(Value.valueset)\
            .filter(ValueSet.contribution_pk == self.obj.pk)\
            .options(
                joinedload(Value.valueset, ValueSet.language),
                joinedload(Value.valueset, ValueSet.parameter),
                joinedload(Value.domainelement),
                joinedload_all(
                    Value.valueset, ValueSet.references, ValueSetReference.source))\
            .order_by(ValueSet.parameter_pk, ValueSet.language_pk, Value.pk)

    def dataset(self, req):
        ds = Dataset('%s-%s-%s' % (
            req.dataset.id, self.obj.__class__.__name__.lower(), self.obj.id))
        cols = self.columns(req)
        ds.fields = tuple(col['name'] if isinstance(col, dict) else col for col in cols)
        ds.table.schema.aboutUrl = get_url_template(req, 'value').replace('{id}', '{ID}')

        for col in cols:
            if isinstance(col, dict):
                name = col.pop('name')
                for attr, value in col.items():
                    setattr(ds.table.schema.columns[name], attr, value)

        ds.metadata['dc:bibliographicCitation '] = text_citation(req, self.obj)
        ds.metadata['dc:publisher'] = '%s, %s' % (
            req.dataset.publisher_name, req.dataset.publisher_place)
        ds.metadata['dc:license'] = req.dataset.license
        ds.metadata['dc:issued'] = req.dataset.published.isoformat()
        ds.metadata['dc:title'] = self.obj.name
        ds.metadata['dc:creator'] = self.obj.formatted_contributors()
        ds.metadata['dc:identifier'] = req.resource_url(self.obj)
        ds.metadata['dc:isPartOf'] = req.resource_url(req.dataset)
        ds.metadata['dcat:accessURL'] = req.route_url('download')

        for value in self.value_query():
            refs, sources = self.refs_and_sources(req, value.valueset)
            ds.sources.add(*sources)
            ds.add_row(self.row(req, value, refs))
        return ds


class CldfDownload(Download):
    ext = 'cldf'
    description = "Dataset in CLDF"

    def iterdatasets(self):
        for contrib in DBSession.query(Contribution) \
            .options(joinedload_all(
                Contribution.contributor_assocs, ContributionContributor.contributor)):
            yield contrib

    def create(self, req, filename=None, verbose=True, outfile=None):
        with safe_overwrite(outfile or self.abspath(req)) as tmp:
            with Archive(tmp, 'w') as zipfile:
                for contrib in self.iterdatasets():
                    ds = req.registry.getAdapter(contrib, ICldfDataset, 'cldf')
                    ds.write(req, zipfile)
                zipfile.write_text(format_readme(req), 'README.txt')
