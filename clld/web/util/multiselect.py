from pyramid.httpexceptions import HTTPFound

from clld.db.meta import DBSession
from clld.db.models.common import Combination, Parameter
from clld.web.util.helpers import JS
from clld.web.util.component import Component


class MultiSelect(Component):
    """A select component based on select2.
    """
    __template__ = 'clld:web/templates/multiselect.mako'

    def __init__(self, req, name, eid, collection=None, url=None, selected=None):
        """
        for selections using remote data pass url, otherwise pass collection.

        :param selected: list of items to be marked as selected or None.
        """
        assert collection or url
        assert not (collection and url)
        self.req = req
        self.collection = collection
        self.url = url
        self.eid = eid
        self.name = name
        self.selected = selected

    def get_default_options(self):
        res = {'placeholder': "Search %s" % self.name, 'width': 'element'}
        if not self.collection:
            res.update(
                minimumInputLength=2,
                multiple=True,
                ajax={
                    'url': self.url,
                    'dataType': 'json',
                    'data': JS('CLLD.MultiSelect.data'),
                    'results': JS('CLLD.MultiSelect.results'),
                }
            )
        return res

    def format_result(self, obj):
        """
        called for each matching result.

        :return: dictionary which can be serialized as JSON for use by the select2 component.
        """
        return {'id': getattr(obj, 'id', obj.pk), 'text': '%s' % getattr(obj, 'label', obj)}

    def render(self, selected=None):
        """allow the list of selected items to be specified upon rendering, too.
        """
        if selected:
            self.selected = selected
        return Component.render(self)


class CombinationMultiSelect(MultiSelect):
    def __init__(self, req, name='parameters', eid='ms-parameters', combination=None,
                 **kw):
        #if 'parameters' in req.params:
        #    id_ = Combination.delimiter.join(req.params['parameters'].split(','))
        #    if not combination or (combination and id_ != combination.id):
        #        raise HTTPFound(req.route_url('combination', id=id_))
        kw['collection'] = self.query().all()
        if combination:
            kw['selected'] = combination.parameters
        MultiSelect.__init__(self, req, name, eid, **kw)

    @classmethod
    def query(cls):
        return DBSession.query(Parameter)

    def format_result(self, obj):
        return {'id': obj.id, 'text': '%s: %s' % (obj.id, obj.name)}

    def get_options(self):
        return {
            'data': [self.format_result(o) for o in self.collection],
            'multiple': True}
