import re
import urllib.parse

from pyramid.request import Request, reify
from pyramid.interfaces import IRoutesMapper
from webob.request import Request as WebobRequest

from clld import RESOURCES
from clld import interfaces
from clld.db.meta import DBSession
from clld.db.models import common


class ClldRequest(Request):

    """Custom Request class."""

    @reify
    def query_params(self):
        """Convenient access to the query parameters of the current request.

        :return: dict of the query parameters of the request URL.
        """
        return {k: v[0] for k, v in
                urllib.parse.parse_qs(urllib.parse.urlparse(self.url).query).items()}

    @property
    def db(self):
        """Convenient access to the db session.

        We make the db session available as request attribute, so we do not have to
        import it in templates.
        """
        return DBSession

    @reify
    def dataset(self):
        """Convenient access to the Dataset object.

        Properties of the :py:class:`clld.db.models.common.Dataset` object an
        application serves are used in various places, so we want to have a reference to
        it.
        """
        return self.db.query(common.Dataset).first()

    @property
    def contact_email_address(self):
        if 'clld.contact' in self.registry.settings:
            return self.registry.settings['clld.contact']
        return self.dataset.contact  # pragma: no cover

    def get_datatable(self, name, model, **kw):
        """Convenient lookup and retrieval of initialized DataTable object.

        :param name: Name under which the datatable class was registered.
        :param model: model class to pass as initialization parameter to the datatable.
        :param kw:
            Keyword parameters are passed through to the initialization of the datatable.
        :return:
            :py:class:`clld.web.datatables.base.DataTable` instance, if a datatable was
            registered for ``name``.
        """
        dt = self.registry.queryUtility(interfaces.IDataTable, name=name)
        if dt:
            return dt(self, model, **kw)

    def get_map(self, name=None, **kw):
        """Convenient lookup and retrieval of initialized Map object.

        :param name: Name under which the map was registered.
        :return:
            :py:class:`clld.web.maps.Map` instance, if a map was registered else ``None``.
        """
        if name is None and self.matched_route:
            name = self.matched_route.name
        if name:
            map_ = self.registry.queryUtility(interfaces.IMap, name=name)
            if map_:
                return map_(self.context, self, **kw)

    def _route(self, obj, rsc, **kw):
        """Determine the name of the canonical route for a resource instance.

        The resource may be specified as object or as mapper class and id.

        :return:
            pair (route_name, kw) suitable as arguments for the Request.route_url method.
        """
        if rsc is None:
            for _rsc in RESOURCES:
                if _rsc.interface.providedBy(obj):
                    rsc = _rsc
                    break
            assert rsc

        route = rsc.name
        if 'ext' in kw:
            route += '_alt'

        # if rsc is passed explicitely, we allow the object id to be passed in as obj,
        # to make it possible to create resource URLs without having the "real" object.
        kw.setdefault('id', getattr(obj, 'id', obj))
        return route, kw

    def ctx_for_url(self, url):
        """Method to reverse URL generation for resources.

        I.e. given a URL, tries to determine the associated resource.

        :return: model instance or ``None``.
        """
        mapper = self.registry.getUtility(IRoutesMapper)
        _path = urllib.parse.urlparse(url).path
        info = mapper(WebobRequest({'PATH_INFO': _path}))
        if not info['route']:
            # FIXME: hack to cater to deployments under a path prefix
            info = mapper(WebobRequest({'PATH_INFO': re.sub(r'^/[a-z]+', '', _path)}))
        if info['route']:
            for rsc in RESOURCES:
                if rsc.name == info['route'].name:
                    if rsc.name == 'dataset':
                        return self.dataset
                    if info['match']:
                        return rsc.model.get(info['match']['id'], default=None)

    def resource_url(self, obj, rsc=None, **kw):
        """Get the absolute URL for a resource.

        :param obj:
            A resource or the id of a resource; in the latter case ``rsc`` must be passed.
        :param rsc: A registered :py:class:`clld.Resource`.
        :param kw:
            Keyword parameters are passed through to
            `pyramid.request.Request.route_url <http://docs.pylonsproject.org/projects/\
            pyramid/en/1.0-branch/api/request.html#pyramid.request.Request.route_url>`_
        :return: URL
        """
        route, kw = self._route(obj, rsc, **kw)
        return self.route_url(route, **kw)

    def route_url(self, route, *args, **kw):
        """Facade for Request.route_url."""
        if '__locale__' in self.params:
            if '_query' not in kw:
                kw['_query'] = {}
            kw['_query']['__locale__'] = self.params['__locale__']
        return Request.route_url(self, route, *args, **kw)

    def resource_path(self, obj, rsc=None, **kw):
        """Determine the path component of a Resource's URL."""
        route, kw = self._route(obj, rsc, **kw)
        return self.route_path(route, **kw)

    def file_ospath(self, file_):
        if 'clld.files' in self.registry.settings:
            return str(self.registry.settings['clld.files'].joinpath(file_.relpath))

    def file_url(self, file_):
        if 'url' in file_.jsondata:
            # just a preparation for full support of non-local files
            return file_.jsondata['url']  # pragma: no cover

        if 'clld.files' in self.registry.settings:
            return self.static_url(self.file_ospath(file_))
