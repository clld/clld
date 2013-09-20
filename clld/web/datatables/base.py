"""
This module provides base classes to compose DataTables, i.e. objects which have a double
nature: On the client they provide the information to instantiate a jquery DataTables
object. Server side they know how to provide the data to the client-side table.
"""
from json import dumps
import re

from sqlalchemy import desc
from sqlalchemy.types import String, Unicode, Float, Integer, Boolean
from pyramid.renderers import render
from markupsafe import Markup
from zope.interface import implementer

from clld.db.meta import DBSession
from clld.db.models.common import Language
from clld.db.util import icontains
from clld.web.util.htmllib import HTML
from clld.web.util.helpers import link, button, icon, JSMap, JS_CLLD
from clld.interfaces import IDataTable, IIndex
from clld.util import cached_property


OPERATOR_PATTERN = re.compile('\s*(?P<op>\>\=?|\<\=?|\=\=?)\s*')


def filter_number(col, qs, type_=None, qs_weight=1):
    """
    :param col: an sqlalchemy column instance.
    :param qs: a string, providing a filter criterion.
    :return: sqlalchemy filter expression.
    """
    op = col.__eq__
    match = OPERATOR_PATTERN.match(qs)
    if match:
        op = {
            '>': col.__gt__,
            '>=': col.__ge__,
            '=': col.__eq__,
            '==': col.__eq__,
            '<': col.__lt__,
            '<=': col.__le__,
        }.get(match.group('op'), col.__eq__)
        qs = qs[match.end():]
    try:
        if type_:
            qs = type_(qs.strip())
        else:
            if isinstance(col.property.columns[0].type, Float):
                qs = float(qs.strip()) * qs_weight
            if isinstance(col.property.columns[0].type, Integer):
                qs = int(qs.strip()) * qs_weight
        return op(qs)
    except ValueError:  # pragma: no cover
        # if we cannot form a proper filter argument, we return None
        return


class Col(object):
    """DataTables are basically a list of column specifications.
    """
    dt_name_pattern = re.compile('[a-z]+[A-Z]+[a-z]+')

    # convenient way to provide defaults for some kw arguments of __init__:
    __kw__ = {}

    def __init__(self, dt, name, **kw):
        self.dt = dt
        self.name = name
        self.js_args = {
            'sName': name,
            'sTitle': '' if not name
            else self.dt.req.translate(name.replace('_', ' ').capitalize())}

        # take the defaults into account:
        for k, v in self.__kw__.items():
            kw.setdefault(k, v)

        for key, val in kw.items():
            if self.dt_name_pattern.match(key):
                self.js_args[key] = val
            else:
                setattr(self, key, val)

        if not hasattr(self, 'model_col'):
            #
            # TODO: fix mechanism to infer model_col for derived classes!)
            #
            self.model_col = None
            model_col = getattr(self.dt.model, self.name, None)
            if model_col and hasattr(model_col.property, 'columns'):
                self.model_col = model_col

        if self.model_col and isinstance(self.model_col.property.columns[0].type, Boolean):
            if not hasattr(self, 'choices'):
                self.choices = ['True', 'False']

    def order(self):
        """called when collecting the order by clauses of a datatable's search query
        """
        return self.model_col

    def search(self, qs):
        """called when collecting the filter criteria of a datatable's search query
        """
        if self.model_col:
            if isinstance(self.model_col.property.columns[0].type, (String, Unicode)):
                if not getattr(self, 'choices', None):
                    return icontains(self.model_col, qs)
                return self.model_col.__eq__(qs)
            if isinstance(self.model_col.property.columns[0].type, (Float, Integer)):
                return filter_number(self.model_col, qs)
            if isinstance(self.model_col.property.columns[0].type, Boolean):
                return self.model_col.__eq__(qs == 'True')

    def format(self, item):
        """called when converting the matching result items of a datatable's search query
        to json.
        """
        if self.model_col:
            if isinstance(self.model_col.property.columns[0].type, Boolean):
                return '%s' % getattr(item, self.model_col.name, '')
            return getattr(item, self.model_col.name, None) or ''
        return getattr(item, self.name, None) or ''


class PercentCol(Col):
    """treats a model col of type float as percentage.
    """
    __kw__ = {'sClass': 'right', 'input_size': 'small'}

    def search(self, qs):
        return filter_number(self.model_col, qs, qs_weight=0.01)

    def format(self, item):
        return '%.0f%%' % (100 * getattr(item, self.model_col.name),)


class LinkCol(Col):
    """Column which renders a link.
    """
    def get_attrs(self, item):
        return {}

    def get_obj(self, item):
        return item

    def format(self, item):
        return link(self.dt.req, self.get_obj(item), **self.get_attrs(item))


class LanguageCol(LinkCol):
    def get_obj(self, item):
        return item.language

    def order(self):
        return Language.name

    def search(self, qs):
        return icontains(Language.name, qs)


class IdCol(LinkCol):
    __kw__ = {'sClass': 'right', 'input_size': 'mini'}

    def get_attrs(self, item):
        return {'label': item.id}


class LinkToMapCol(Col):
    """We use the CLLD.Map.showInfoWindow API function to construct a button to open
    a popup on the map.
    """
    __kw__ = {'bSearchable': False, 'bSortable': False, 'sTitle': ''}

    def get_obj(self, item):
        return item

    def format(self, item):
        obj = self.get_obj(item)
        if not obj or getattr(obj, 'latitude', None) is None:
            return ''
        return HTML.a(
            icon('icon-globe'),
            title='show %s on map' % getattr(obj, 'name', ''),
            href="#map",
            onclick=JS_CLLD.mapShowInfoWindow(None, obj.id),
            class_='btn',
        )


class DetailsRowLinkCol(Col):
    __kw__ = {
        'bSearchable': False,
        'bSortable': False,
        'sClass': 'center',
        'sType': 'html',
        'sTitle': 'Details',
        'button_text': 'more',
    }

    def format(self, item):
        return button(
            self.button_text,
            href=self.dt.req.resource_url(item, ext='snippet.html'),
            title="show details",
            class_="btn-info details",
            tag=HTML.button)


@implementer(IDataTable)
class DataTable(object):
    def __init__(self, req, model, eid=None, **kw):
        """
        :param req: request object.
        :param model: mapper class, instances of this class will be the rows in the table.
        :param eid: HTML element id that will be assigned to this data table.
        """
        self.model = model
        self.req = req
        self.eid = eid or self.__class__.__name__
        self.count_all = None
        self.count_filtered = None

    def __unicode__(self):
        return '%ss' % self.model.mapper_name()

    def __repr__(self):
        return '%ss' % self.model.mapper_name()

    def col_defs(self):
        raise NotImplementedError  # pragma: no cover

    @cached_property()
    def cols(self):
        return self.col_defs()

    def xhr_query(self):
        """
        :return: a mapping to be passed as query parameters to the server when requesting\
        table data via xhr.
        """
        return {}

    @cached_property()
    def options(self):
        opts = {
            'bServerSide': True,
            'bProcessing': True,
            "sDom": "<'dt-before-table row-fluid'<'span4'i><'span6'p><'span2'f<'" + self.eid + "-toolbar'>>r>t<'span4'i><'span6'p>",
            "bAutoWidth": False,
            "sPaginationType": "bootstrap",
            "aoColumns": [col.js_args for col in self.cols],
            "iDisplayLength": 100,
            "aLengthMenu": [[50, 100, 200], [50, 100, 200]],
            'sAjaxSource': self.req.route_url(
            '%ss' % self.model.mapper_name().lower(), _query=self.xhr_query() or {}),
        }
        opts.update(self.get_options())
        #opts.setdefault('sAjaxSource', self.req.url)
        return opts

    def base_query(self, query):
        """Custom DataTables can overwrite this method to add joins, or apply filters.
        """
        return query

    def render(self):
        return Markup(render(
            'clld:web/templates/datatable.mako',
            {'datatable': self, 'options': Markup(dumps(self.options))},
            request=self.req))

    def get_query(self, limit=1000, offset=0):
        query = self.base_query(DBSession.query(self.model))
        self.count_all = query.count()

        for name, val in self.req.params.items():
            if val and name.startswith('sSearch_'):
                try:
                    clause = self.cols[int(name.split('_')[1])].search(val)
                except ValueError:  # pragma: no cover
                    clause = None
                if clause is not None:
                    query = query.filter(clause)

        self.count_filtered = query.count()

        for index in range(int(self.req.params.get('iSortingCols', 0))):
            col = self.cols[int(self.req.params['iSortCol_%s' % index])]
            if col.js_args.get('bSortable', True):
                orders = col.order()
                if orders is not None:
                    if not isinstance(orders, (tuple, list)):
                        orders = [orders]
                    for order in orders:
                        if self.req.params.get('sSortDir_%s' % index) == 'desc':
                            order = desc(order)
                        query = query.order_by(order)

        query = query.order_by(self.model.pk)
        if 'iDisplayLength' in self.req.params:
            # make sure no more than 1000 items can be selected
            limit = min([int(self.req.params['iDisplayLength']), 1000])
        query = query\
            .limit(limit if limit != -1 else 1000)\
            .offset(int(self.req.params.get('iDisplayStart', offset)))
        return query

    def toolbar(self):
        """
        """
        return HTML.div(
            HTML.a(
                icon('download-alt'),
                HTML.span(class_="caret"),
                **{
                    'class_': "btn dropdown-toggle",
                    'data-toggle': "dropdown",
                    'href': "#",
                    'id': "dt-dl-opener",
                }
            ),
            HTML.ul(
                #HTML.li(HTML.a('csv', href="#")),
                *[HTML.li(HTML.a(
                    fmt,
                    href="#",
                    onclick="document.location.href = CLLD.DataTable.current_url('%s', '%s'); return false;" % (self.eid, fmt),
                    id='dt-dl-%s' % fmt))
                  for fmt in [a.extension for n, a in self.req.registry.getAdapters([self.model()], IIndex)] if fmt != 'html'],
                **dict(class_="dropdown-menu")),
            button(icon('info-sign', inverted=True), class_='btn-info %s-cdOpener' % self.eid),
            class_='btn-group right')

    def get_options(self):
        return {}
