from json import dumps
import re

from sqlalchemy import asc, desc, or_
from sqlalchemy.types import String, Unicode, Float, Integer
from pyramid.renderers import render
from markupsafe import Markup

from clld.db.meta import DBSession
from clld.web.util.htmllib import tag


class Col(object):
    dt_name_pattern = re.compile('[a-z]+[A-Z]+[a-z]+')
    operator_pattern = re.compile('\s*(?P<op>\>\=?|\<\=?|\=\=?)\s*')

    def __init__(self, dt, name, **kw):
        self.dt = dt
        self.name = name
        self.js_args = {
            'sName': name,
            'sTitle': name.capitalize(),
            'bSortable': True,
            'bSearchable': True,
            'bVisible': True,
        }
        for key, val in kw.items():
            if self.dt_name_pattern.match(key):
                self.js_args[key] = val
            else:
                setattr(self, key, val)

        if not hasattr(self, 'model_col'):
            self.model_col = None
            model_col = getattr(self.dt.model, self.name, None)
            if model_col and hasattr(model_col.property, 'columns'):
                self.model_col = model_col

    def order(self, direction):
        if self.model_col:
            return desc(self.model_col) if direction == 'desc' else asc(self.model_col)

    def search(self, qs):
        if self.model_col:
            if isinstance(self.model_col.property.columns[0].type, (String, Unicode)):
                return self.model_col.contains(qs)
            if isinstance(self.model_col.property.columns[0].type, (Float, Integer)):
                op = self.model_col.__eq__
                match = self.operator_pattern.match(qs)
                if match:
                    op = {
                        '>': self.model_col.__gt__,
                        '>=': self.model_col.__ge__,
                        '=': self.model_col.__eq__,
                        '==': self.model_col.__eq__,
                        '<': self.model_col.__lt__,
                        '<=': self.model_col.__le__,
                    }.get(match.group('op'), self.model_col.__eq__)
                    qs = qs[match.end():]
                try:
                    if isinstance(self.model_col.property.columns[0].type, Float):
                        qs = float(qs.strip())
                    if isinstance(self.model_col.property.columns[0].type, Integer):
                        qs = int(qs.strip())
                    return op(qs)
                except ValueError:
                    pass

    def format(self, item):
        return getattr(item, self.name, None)

    #
    # TODO: how to pass function as mRender attribute? JsSymbol class?
    # 'mRender': clld.renderers["name"]?
    #


class LinkCol(Col):
    def __init__(self, dt, name, route_name=None, get_label=None, get_attrs=None, **kw):
        self._get_label = get_label
        self._get_attrs = get_attrs
        kw.setdefault('sType', 'html')
        self.route_name = route_name or name
        Col.__init__(self, dt, name, **kw)

    def get_label(self, item):
        if self._get_label:
            return self._get_label(item)
        return getattr(item, self.name, item.id)

    def get_attrs(self, item):
        res = {'href': self.dt.req.route_url(self.route_name, id=item.id)}
        if self._get_attrs:
            res.update(self._get_attrs(item))
        return res

    def format(self, item):
        return tag('a', self.get_label(item), **self.get_attrs(item))


class DetailsRowLinkCol(Col):
    def __init__(self, dt, name=None, route_name=None, **kw):
        kw.setdefault('bSortable', False)
        kw.setdefault('bSearchable', False)
        kw.setdefault('sClass', 'center')
        kw.setdefault('sType', 'html')
        name = name or ''
        self.route_name = route_name or name
        if not self.route_name.endswith('_alt'):
            self.route_name = self.route_name + '_alt'
        Col.__init__(self, dt, name, **kw)

    def format(self, item):
        return tag(
            'span', ' ',
            class_='ui-icon ui-icon-circle-plus',
            href=self.dt.req.route_url(self.route_name, ext='snippet.html', id=item.id))


class IdCol(Col):
    def __init__(self, dt, name='id', **kw):
        kw.setdefault('bVisible', False)
        kw.setdefault('bSearchable', False)
        Col.__init__(self, dt, name, **kw)


class DataTable(object):
    show_details = False
    search = 'col'  # col|global|global_col

    def __init__(self, req, model, eid=None):
        self.model = model
        self.req = req
        self.eid = eid or self.__class__.__name__
        self._cols = None
        self._options = None
        self.count_all = None
        self.count_filtered = None
        self.server_side = False

    def col_defs(self):
        return [
            IdCol(self),
            Col(self, 'name'),
        ]

    @property
    def cols(self):
        if not self._cols:
            self._cols = self.col_defs()
        return self._cols

    @property
    def options(self):
        if not self._options:
            self._options = self.get_options()
            if self._options.get('bServerSide'):
                self.server_side = True
                self._options['bProcessing'] = True
                if 'sAjaxSource' not in self._options:
                    self._options['sAjaxSource'] = self.req.url
        return self._options

    def base_query(self, query):
        return query

    def render(self):
        return Markup(render(
            'clld:web/templates/datatable.mako',
            {'datatable': self, 'options': Markup(dumps(self.options))},
            request=self.req))


    def get_query(self, limit=200, offset=0):
        query = self.base_query(DBSession.query(self.model))
        self.count_all = query.count()

        # single search box:
        if self.search.startswith('global'):
            qs = self.req.params.get('sSearch')
            if qs:
                if self.search == 'global_col':
                    try:
                        clause = self.cols[int(self.req.params.get('searchCol'))].search(qs)
                    except ValueError:
                        clause = None
                    if clause is not None:
                        query = query.filter(clause)
                else:
                    clauses = []
                    for col in self.cols:
                        if col.js_args['bSearchable']:
                            clauses.append(col.search(qs))
                    query = query.filter(or_(*[c for c in clauses if c is not None]))
        # search box per column:
        else:
            for name, val in self.req.params.items():
                if val and name.startswith('sSearch_'):
                    try:
                        clause = self.cols[int(name.split('_')[1])].search(val)
                    except ValueError:
                        clause = None
                    if clause is not None:
                        query = query.filter(clause)

        self.count_filtered = query.count()

        for index in range(int(self.req.params.get('iSortingCols', 0))):
            col = self.cols[int(self.req.params['iSortCol_%s' % index])]
            if col.js_args['bSortable']:
                order = col.order(self.req.params['sSortDir_%s' % index])
                if order is not None:
                    query = query.order_by(order)

        query = query.order_by(self.model.pk)
        query = query\
            .limit(int(self.req.params.get('iDisplayLength', limit)))\
            .offset(int(self.req.params.get('iDisplayStart', offset)))
        return query

    def toolbar(self):
        if self.search == 'global_col':
            return Markup(
                tag('select',
                    *[tag('option', col.js_args['sTitle'], value=str(i))
                      for i, col in enumerate(self.cols) if col.js_args['bSearchable']],
                    id='searchCol'))
        else:
            return ''

    def get_options(self):
        return {
            "bServerSide": True,
            "aoColumns": [col.js_args for col in self.cols],
            "iDisplayLength": 25,
            "aLengthMenu": [[25, 50, 100], [25, 50, 100]],
            #"sPaginationType": "bootstrap",
        }
#            "bProcessing": False,
#            "bServerSide": False,
#            "sAjaxSource": "${request.url}",
#            "bPaginate": True,
#            "sPaginationType": "full_numbers"
#            "bLengthChange": True,
#            "bFilter": True,
#            "bSort": True,
#            "bInfo": True,
#            "bAutoWidth": True,
#
#            "bStateSave": True,
#
#
#"aLengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]]
#
#            "aoColumnDefs": [
#            {
#                // `data` refers to the data for the cell (defined by `mData`, which
#                // defaults to the column being worked with, in this case is the first
#                // Using `row[0]` is equivalent.
#                "mRender": function ( data, type, row ) {
#                    return data +' '+ row[3];
#                },
#                "aTargets": [ 0 ]
#            },
#            { "bVisible": false,  "aTargets": [ 3 ] },
#            { "sClass": "center", "aTargets": [ 4 ] }
#        ]
#
#
#
#"aoColumns": [
#      { "aDataSort": [ 0, 1 ] , "asSorting": ["asc", "desc" ], "bSearchable": true, "bSortable": true, "bVisible": true, sName, sClass, sTitle
#        sType: string|numeric|date|html, sWidth},
#      { "aDataSort": [ 1, 0 ] },
#      { "aDataSort": [ 2, 3, 4 ] },
#      null,
#      null
#    ]
#
#
#        }
#
#
#$('#example tbody tr').live('click', function () {
#        var sTitle;
#        var nTds = $('td', this);
#        var sBrowser = $(nTds[1]).text();
#        var sGrade = $(nTds[4]).text();
#
#        if ( sGrade == "A" )
#            sTitle =  sBrowser+' will provide a first class (A) level of CSS support.';
#        else if ( sGrade == "C" )
#            sTitle = sBrowser+' will provide a core (C) level of CSS support.';
#        else if ( sGrade == "X" )
#            sTitle = sBrowser+' does not provide CSS support or has a broken implementation. Block CSS.';
#        else
#            sTitle = sBrowser+' will provide an undefined level of CSS support.';
#
#        alert( sTitle )
#    } );
#
#
#
##
## js: http://jqueryui.com/autocomplete/#categories
##
