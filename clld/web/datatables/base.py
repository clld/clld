"""
This module provides base classes to compose DataTables, i.e. objects which have a double
nature: On the client they provide the information to instantiate a jquery DataTables
object. Server side they know how to provide the data to the client-side table.
"""
import re

from sqlalchemy import desc
from sqlalchemy.types import String, Unicode, Float, Integer, Boolean
from sqlalchemy.sql.expression import cast
from zope.interface import implementer

from clld.db.meta import DBSession
from clld.db.util import icontains
from clld.web.util.htmllib import HTML
from clld.web.util.helpers import link, button, icon, JS_CLLD, external_link
from clld.web.util.component import Component
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

    A column in a DataTable typically corresponds to a column of an sqlalchemy model.
    This column can either be supplied directly via a model_col keyword argument, or we
    try to look it up as attribute with name "name" on self.dt.model.
    """
    dt_name_pattern = re.compile('[a-z]+[A-Z]+[a-z]+')

    # convenient way to provide defaults for some kw arguments of __init__:
    __kw__ = {}

    def __init__(self, dt, name, get_object=None, model_col=None, format=None, **kw):
        self.dt = dt
        self.name = name
        self._get_object = get_object
        self._format = format
        self.model_col = model_col
        self.model_col_type = None
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

        if not self.model_col:
            #
            # model_col was not explicitely passed as keyword parameter
            #
            # TODO: fix mechanism to infer model_col for derived classes!)
            #
            model_col = getattr(self.dt.model, self.name, None)
            if model_col and hasattr(model_col.property, 'columns'):
                self.model_col = model_col

        if self.model_col:
            self.model_col_type = self.model_col.property.columns[0].type

        if isinstance(self.model_col_type, Boolean):
            if not hasattr(self, 'choices'):
                self.choices = ['True', 'False']
            if not hasattr(self, 'input_size'):
                self.input_size = 'small'
        elif isinstance(self.model_col_type, (Float, Integer)):
            self.js_args.setdefault('sClass', 'right')
            if not hasattr(self, 'input_size'):
                self.input_size = 'small'

    def get_obj(self, item):
        """derived columns with a model_col not on self.dt.model should override this
        method.
        """
        if getattr(self, '_get_object'):
            return self._get_object(item)
        return item

    def get_value(self, item):
        mc = self.model_col
        val = getattr(self.get_obj(item), mc.name if mc else self.name, None)
        return '' if val is None else val

    def format_value(self, value):
        if isinstance(self.model_col_type, Boolean):
            return '%s' % value
        if isinstance(self.model_col_type, Float) and isinstance(value, float):
            return ('%.' + str(getattr(self, 'precision', 2)) + 'f') % value
        return value

    #
    # external API called by DataTable objects:
    #
    def order(self):
        """called when collecting the order by clauses of a datatable's search query
        """
        return self.model_col

    def search(self, qs):
        """called when collecting the filter criteria of a datatable's search query
        """
        if isinstance(self.model_col_type, (String, Unicode)):
            if getattr(self, 'choices', None):
                # make sure select box values match sharp!
                return self.model_col.__eq__(qs)
            else:
                return icontains(self.model_col, qs)
        if isinstance(self.model_col_type, (Float, Integer)):
            return filter_number(self.model_col, qs)
        if isinstance(self.model_col_type, Boolean):
            return self.model_col.__eq__(qs == 'True')

    def format(self, item):
        """called when converting the matching result items of a datatable's search query
        to json.
        """
        if getattr(self, '_format'):
            return self._format(item)
        return self.format_value(self.get_value(item))


class ExternalLinkCol(Col):
    __kw__ = {'bSearchable': False, 'bSortable': False}

    def get_attrs(self, item):
        return {}

    def format(self, item):
        url = getattr(self.get_obj(item), 'url', None)
        return external_link(url, **self.get_attrs(item)) if url else ''


class PercentCol(Col):
    """treats a model col of type float as percentage.
    """
    def search(self, qs):
        return filter_number(self.model_col, qs, qs_weight=0.01)

    def format_value(self, value):
        return '%.0f%%' % (100 * value,)


class LinkCol(Col):
    """Column which renders a link.
    """
    def get_attrs(self, item):
        return {}

    def format(self, item):
        obj = self.get_obj(item)
        return link(self.dt.req, obj, **self.get_attrs(item)) if obj else ''


class IdCol(LinkCol):
    __kw__ = {'sClass': 'right', 'input_size': 'mini'}

    def get_attrs(self, item):
        return {'label': self.get_obj(item).id}

    def search(self, qs):
        if self.model_col:
            return self.model_col.__eq__(qs)


class IntegerIdCol(IdCol):
    __kw__ = {'input_size': 'mini', 'sClass': 'right', 'sTitle': 'No.'}

    def search(self, qs):
        return filter_number(cast(self.model_col, Integer), qs, type_=int)

    def order(self):
        return cast(self.model_col, Integer)


class LinkToMapCol(Col):
    """We use the CLLD.Map.showInfoWindow API function to construct a button to open
    a popup on the map.
    """
    __kw__ = {'bSearchable': False, 'bSortable': False, 'sTitle': '', 'map_id': 'map'}

    def format(self, item):
        obj = self.get_obj(item)
        if not obj or getattr(obj, 'latitude', None) is None:
            return ''
        return HTML.a(
            icon('icon-globe'),
            title='show %s on map' % getattr(obj, 'name', ''),
            href="#" + self.map_id,
            onclick=JS_CLLD.mapShowInfoWindow(self.map_id, obj.id),
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
            href=self.dt.req.resource_url(self.get_obj(item), ext='snippet.html'),
            title="show details",
            class_="btn-info details",
            tag=HTML.button)


@implementer(IDataTable)
class DataTable(Component):
    """DataTables are used to manage (sort, filter, display) lists of instances of one
    model class.

    Often datatables are used to display only a pre-filtered set of items which are
    related to some other entity in the system. This scenario is supported as follows:
    For each model class listed in
    :py:attr:`clld.web.datatables.base.DataTable.__constraints__` an appropriate object
    specified either by keyword parameter or as request parameter will be looked up at
    datatable initialization, and placed into a datatable attribute named after the model
    class in lowercase. These attributes will be used when creating the URL for the data
    request, to make sure the same pre-filtering is applied.

    .. note::

         The actual filtering has to be done in a custom implementation of
         :py:meth:`clld.web.datatables.base.DataTable.base_query`.

     """
    __template__ = 'clld:web/templates/datatable.mako'
    __constraints__ = []

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

        for _model in self.__constraints__:
            attr = self.attr_from_constraint(_model)
            if kw.get(attr):
                setattr(self, attr, kw[attr])
            elif attr in req.params:
                setattr(self, attr, _model.get(req.params[attr], default=None))
            else:
                setattr(self, attr, None)

    @staticmethod
    def attr_from_constraint(model):
        return model.mapper_name().lower()

    def __unicode__(self):
        return '%ss' % self.model.mapper_name()

    def __repr__(self):
        return '%ss' % self.model.mapper_name()

    def col_defs(self):
        """Must be implemented by derived classes.

        :return: list of instances of :py:class:`clld.web.datatables.base.Col`.
        """
        raise NotImplementedError  # pragma: no cover

    @cached_property()
    def cols(self):
        return self.col_defs()

    def xhr_query(self):
        """
        :return: a mapping to be passed as query parameters to the server when requesting\
        table data via xhr.
        """
        res = {}
        for _model in self.__constraints__:
            attr = self.attr_from_constraint(_model)
            if getattr(self, attr):
                res[attr] = getattr(self, attr).id
        return res

    def get_default_options(self):
        query_params = {}
        query_params.update(self.req.query_params)
        query_params.update(self.xhr_query() or {})
        return {
            'bServerSide': True,
            'bProcessing': True,
            "sDom": "<'dt-before-table row-fluid'<'span4'i><'span6'p><'span2'f<'"
            + self.eid + "-toolbar'>>r>t<'span4'i><'span6'p>",
            "bAutoWidth": False,
            "sPaginationType": "bootstrap",
            "aoColumns": [col.js_args for col in self.cols],
            "iDisplayLength": 100,
            "aLengthMenu": [[50, 100, 200], [50, 100, 200]],
            'sAjaxSource': self.req.route_url(
                '%ss' % self.model.mapper_name().lower(), _query=query_params),
        }

    def base_query(self, query):
        """Custom DataTables can overwrite this method to add joins, or apply filters.

        :return: ``sqlalchemy.orm.query.Query`` instance.
        """
        return query

    def default_order(self):
        return self.model.pk

    def get_query(self, limit=1000, offset=0):
        query = self.base_query(
            DBSession.query(self.model).filter(self.model.active == True))
        self.count_all = query.count()

        for name, val in self.req.params.items():
            if val and name.startswith('sSearch_'):
                try:
                    clause = self.cols[int(name.split('_')[1])].search(val)
                except (ValueError, IndexError):  # pragma: no cover
                    clause = None
                if clause is not None:
                    query = query.filter(clause)

        self.count_filtered = query.count()

        try:
            iSortingCols = int(self.req.params.get('iSortingCols', 0))
        except ValueError:
            iSortingCols = 0

        for index in range(iSortingCols):
            try:
                col = self.cols[int(self.req.params.get('iSortCol_%s' % index))]
            except (TypeError, ValueError, IndexError):  # pragma: no cover
                continue
            if col.js_args.get('bSortable', True):
                orders = col.order()
                if orders is not None:
                    if not isinstance(orders, (tuple, list)):
                        orders = [orders]
                    for order in orders:
                        if self.req.params.get('sSortDir_%s' % index) == 'desc':
                            order = desc(order)
                        query = query.order_by(order)

        query = query.order_by(self.default_order())
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
            button(
                icon('info-sign', inverted=True),
                class_='btn-info %s-cdOpener' % self.eid),
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
                    onclick="document.location.href = CLLD.DataTable.current_url"
                    "('%s', '%s'); return false;" % (self.eid, fmt),
                    id='dt-dl-%s' % fmt))
                  for fmt in
                  [a.extension for n, a in
                   self.req.registry.getAdapters([self.model()], IIndex)]
                  if fmt != 'html'],
                **dict(class_="dropdown-menu")),
            class_='btn-group right')
