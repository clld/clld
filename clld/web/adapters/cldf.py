from __future__ import unicode_literals
from zipfile import ZipFile, ZIP_DEFLATED
import json

from sqlalchemy import true
from sqlalchemy.orm import joinedload, joinedload_all
from clldutils.path import Path, remove, move
from clldutils.dsv import UnicodeWriter

from clld.web.adapters.download import Download, README
from clld.web.adapters.md import TxtCitation
from clld.web.adapters.csv import CsvmJsonAdapter
from clld.db.meta import DBSession
from clld.db.models.common import (
    Value, ValueSet, ValueSetReference, Parameter, Language, LanguageIdentifier, Source,
)
from clld.db.util import page_query
from clld.lib.bibtex import Database


class CldfDownload(Download):
    ext = 'cldf'
    description = "Dataset in CLDF"

    @staticmethod
    def route_url_pattern(req, route, id=None):
        res = req.route_url(route, id='---').replace('---', '{0}')
        if id:
            return res.format(id)
        return res

    def get_languages(self, req, language_url_pattern):
        q = DBSession.query(Language).filter(Language.active == true()).options(
            joinedload(Language.languageidentifier, LanguageIdentifier.identifier))
        for l in page_query(q):
            yield {
                '@id': language_url_pattern.format(l.id),
                'dc:title': l.name,
                'dc:identifier': [
                    {'@id': i.url(), 'schema:name': i.name}
                    for i in l.identifiers if i.url()],
            }

    def format_sources(self, v):
        # Note: If the value object does have an attribute `references`,
        # this is preferred!
        for ref in getattr(v, 'references', v.valueset.references):
            if ref.source:
                text = ref.source.id
                if ref.description:
                    text += '[%s]' % ref.description
                yield text

    def get_values(self, p, language_url_pattern):
        q = DBSession.query(Value).join(Value.valueset)\
            .filter(ValueSet.parameter_pk == p.pk)\
            .options(
            joinedload(Value.valueset, ValueSet.language),
            joinedload(Value.valueset, ValueSet.contribution),
            joinedload(Value.domainelement),
            joinedload_all(Value.valueset, ValueSet.references, ValueSetReference.source)
        ).order_by(ValueSet.parameter_pk, ValueSet.language_pk, Value.pk)

        with UnicodeWriter() as writer:
            writer.writerow([
                'ID',
                'Language_ID',
                'Parameter_ID',
                'Contribution_ID',
                'Value',
                'Source',
                'Comment',
            ])
            for v in page_query(q):
                writer.writerow([
                    v.id,
                    language_url_pattern.format(v.valueset.language.id),
                    p.id,
                    v.valueset.contribution.id,
                    v.domainelement.name if v.domainelement else v.name,
                    ';'.join(self.format_sources(v)),
                    getattr(v, 'comment', v.valueset.source) or '',
                ])

        return writer.read()

    def create(self, req, filename=None, verbose=True):
        p = self.abspath(req)
        if not p.parent.exists():  # pragma: no cover
            p.parent.mkdir()
        tmp = Path('%s.tmp' % p)

        language_url_pattern = self.route_url_pattern(req, 'language')

        with ZipFile(tmp.as_posix(), 'w', ZIP_DEFLATED) as zipfile:
            tables = []
            for param in DBSession.query(Parameter).options(joinedload(Parameter.domain)):
                fname = '%s-%s.csv' % (req.dataset.id, param.id)
                zipfile.writestr(fname, self.get_values(param, language_url_pattern))
                tables.append({
                    '@type': 'Table',
                    'url': fname,
                    'notes': [
                        {
                            '@id': req.resource_url(param),
                            'dc:identifier': param.id,
                            'dc:title': param.name,
                            'dc:description': param.description or ''}] + [
                        {
                            '@type': 'DomainElement',
                            'name': de.name,
                            'description': de.description,
                            'numeric': de.number
                        } for de in param.domain
                    ],
                })

            md = CsvmJsonAdapter.csvm_basic_doc(req, tables=tables)
            md.update({
                '@type': 'TableGroup',
                'dc:language': list(self.get_languages(req, language_url_pattern)),
                'tableSchema': {
                    "columns": [
                        {
                            "name": "ID",
                            "datatype": "string",
                            "required": True
                        },
                        {
                            "name": "Language_ID",
                            "datatype": "string",
                            "required": True
                        },
                        {
                            "name": "Parameter_ID",
                            "datatype": "string",
                            "required": True
                        },
                        {
                            "name": "Contribution_ID",
                            "datatype": "string",
                            "required": True
                        },
                        {
                            "name": "Value",
                            "datatype": "string",
                            "required": True
                        },
                        {
                            "name": "Source",
                            "datatype": "string",
                        },
                        {
                            "name": "Comment",
                            "datatype": "string",
                        },
                    ],
                    "primaryKey": "ID",
                    'aboutUrl': self.route_url_pattern(req, 'value', '{ID}'),
                },
            })
            zipfile.writestr(
                '%s.csv-metadata.json' % req.dataset.id, json.dumps(md, indent=4))
            bib = Database([
                rec.bibtex() for rec in DBSession.query(Source).order_by(Source.name)])
            zipfile.writestr('%s.bib' % req.dataset.id, ('%s' % bib).encode('utf8'))
            zipfile.writestr(
                'README.txt',
                README.format(
                    req.dataset.name,
                    '=' * (
                        len(req.dataset.name)
                        + len(' data download')),
                    req.dataset.license,
                    TxtCitation(None).render(req.dataset, req)).encode('utf8'))
        if p.exists():  # pragma: no cover
            remove(p)
        move(tmp, p)
