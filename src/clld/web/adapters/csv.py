"""
Serialize clld objects as csv.

We also provide metadata following the guidelines of

- http://www.w3.org/TR/tabular-data-model/ version
  http://www.w3.org/TR/2015/CR-tabular-data-model-20150716/
- http://www.w3.org/TR/tabular-metadata/ version
  http://www.w3.org/TR/2015/CR-tabular-metadata-20150716/
"""
from __future__ import unicode_literals, print_function, division, absolute_import
from itertools import chain

from sqlalchemy import types, Column
from sqlalchemy.inspection import inspect
from pyramid.renderers import render as pyramid_render
from csvw.dsv import UnicodeWriter

from clld.web.adapters.base import Index

QUERY_LIMIT = 2000


class CsvAdapter(Index):

    """Represent tables as csv files (maximal %d rows)."""

    __doc__ %= QUERY_LIMIT

    extension = 'csv'
    mimetype = 'text/csv'
    content_type_params = dict(header='present')

    def render(self, ctx, req):
        with UnicodeWriter() as writer:
            rows = iter(ctx.get_query(limit=QUERY_LIMIT))
            first = next(rows, None)
            if first is not None:
                cols = first.csv_head()
                writer.writerow(cols)
                for item in chain([first], rows):
                    writer.writerow(item.to_csv(ctx=ctx, req=req, cols=cols))
            return writer.read()

    def render_to_response(self, ctx, req):
        res = super(CsvAdapter, self).render_to_response(ctx, req)
        res.content_disposition = 'attachment; filename="%s.csv"' % repr(ctx)
        return res


class CsvmJsonAdapter(Index):

    """Metadata for tabular data serialited as csv.

    .. seealso:: http://www.w3.org/TR/tabular-metadata/
    """

    extension = 'csv-metadata.json'
    mimetype = 'application/csvm+json'
    send_mimetype = 'application/csvm+json'
    rel = 'describedby'

    type_map = [
        (types.Integer, 'http://www.w3.org/2001/XMLSchema#int'),
        (types.Float, 'http://www.w3.org/2001/XMLSchema#float'),
        (types.Boolean, 'http://www.w3.org/2001/XMLSchema#boolean'),
        (types.DateTime, 'http://www.w3.org/2001/XMLSchema#dateTime'),
        (types.Date, 'http://www.w3.org/2001/XMLSchema#date'),
        (types.Unicode, 'http://www.w3.org/2001/XMLSchema#string'),
        (types.String, 'http://www.w3.org/2001/XMLSchema#string'),
    ]

    @classmethod
    def csvm_basic_doc(cls, req, **kw):
        doc = {
            "@context": ["http://www.w3.org/ns/csvw", {"@language": "en"}],
            "dc:publisher": {
                "schema:name": req.dataset.publisher_name,
                "schema:url": {"@id": req.dataset.publisher_url}
            },
            "dc:license": {"schema:name": req.dataset.license}
        }
        if req.dataset.jsondata.get('license_url'):
            doc["dc:license"]["@id"] = req.dataset.jsondata.get('license_url')
        for k, v in kw.items():
            doc[k] = v
        return doc

    @classmethod
    def csvm_doc(cls, url, req, cols):
        primary_key = None
        foreign_keys = []
        columns = []

        for name, col in cols:
            spec = {
                'name': name,
                'datatype': {'@id': 'http://www.w3.org/2001/XMLSchema#string'}}
            if isinstance(col, property):
                col = None  # pragma: no cover
            else:
                if col is not None and not isinstance(col, Column):
                    try:
                        col = col.property.columns[0]
                    except AttributeError:  # pragma: no cover
                        col = None
                        raise
            if col is not None:
                if len(col.foreign_keys) == 1:
                    fk = list(col.foreign_keys)[0]
                    foreign_keys.append({
                        'columnReference': name,
                        'reference': {
                            'resource': fk.column.table.name,
                            'columnReference': fk.column.name}
                    })
                if col.primary_key:
                    primary_key = name
                for t, s in cls.type_map:
                    if isinstance(col.type, t):
                        spec['datatype']['@id'] = s
                        break
                if col.doc:
                    spec['dc:description'] = col.doc
            columns.append(spec)
        tableSchema = {'columns': columns}
        if primary_key:
            tableSchema['primaryKey'] = primary_key
        if foreign_keys:
            tableSchema['foreignKeys'] = foreign_keys
        return cls.csvm_basic_doc(req, url=url, tableSchema=tableSchema)

    def render(self, ctx, req):
        item = ctx.get_query(limit=1).first()
        fields = item.csv_head() if item else []
        cls = inspect(item).class_ if item else None
        doc = self.csvm_doc(
            req.url.replace('.csv-metadata.json', '.csv'),
            req,
            [(field, getattr(cls, field, None)) for field in fields])
        doc["dc:title"] = "{0} - {1}".format(req.dataset.name, ctx)
        return pyramid_render('json', doc, request=req)
