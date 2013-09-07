from markupsafe import Markup
from pyramid.renderers import render
from sqlalchemy.orm import class_mapper

from clld.web.util.helpers import JS, dumps


class MultiSelect(object):
    def __init__(self, req, name, eid, collection=None, url=None):
        assert collection or url
        assert not (collection and url)
        self.req = req
        self.collection = collection
        self.url = url
        self.eid = eid
        self.name = name
        self._options = None

    @property
    def options(self):
        if not self._options:
            self._options = self.get_options()
        return self._options

    def get_options(self):
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
        return {'id': getattr(obj, 'id', obj.pk), 'text': '%s' % obj}

    def render(self, selected=None):
        return Markup(render(
            'clld:web/templates/multiselect.mako',
            {
                'multiselect': self,
                'selected': selected or [],
                'options': Markup(dumps(self.options)),
            },
            request=self.req))
