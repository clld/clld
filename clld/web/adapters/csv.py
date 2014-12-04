"""Serialize clld objects as csv."""
from __future__ import unicode_literals, print_function, division, absolute_import
from itertools import chain

from sqlalchemy import types
from sqlalchemy.inspection import inspect
from pyramid.renderers import render as pyramid_render

from clld.web.adapters.base import Index
from clld.lib.dsv import UnicodeWriter

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


class JsonTableSchemaAdapter(Index):

    """Schema for the columns in a table.

    Renders tables as
    `JSON table schema <http://dataprotocols.org/json-table-schema/>`_

    .. seealso:: http://csvlint.io/about
    """

    extension = 'csv.csvm'
    mimetype = 'application/csvm+json'
    send_mimetype = 'application/json'
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

    def render(self, ctx, req):
        fields = []
        primary_key = None
        foreign_keys = []
        item = ctx.get_query(limit=1).first()
        if item:
            cls = inspect(item).class_

            for field in item.csv_head():
                spec = {
                    'name': field,
                    'constraints': {'type': 'http://www.w3.org/2001/XMLSchema#string'}}
                col = getattr(cls, field, None)
                if col:
                    try:
                        col = col.property.columns[0]
                    except AttributeError:  # pragma: no cover
                        col = None
                if col is not None:
                    if len(col.foreign_keys) == 1:
                        fk = list(col.foreign_keys)[0]
                        foreign_keys.append({
                            'fields': field,
                            'reference': {
                                'resource': fk.column.table.name,
                                'fields': fk.column.name}
                        })
                    if col.primary_key:
                        primary_key = field
                    for t, s in self.type_map:
                        if isinstance(col.type, t):
                            spec['constraints']['type'] = s
                            break
                    spec['constraints']['unique'] = bool(col.primary_key or col.unique)
                    if col.doc:
                        spec['description'] = col.doc
                fields.append(spec)
        doc = {'fields': fields}
        if primary_key:
            doc['primaryKey'] = primary_key
        if foreign_keys:
            doc['foreignKeys'] = foreign_keys
        return pyramid_render('json', doc, request=req)
