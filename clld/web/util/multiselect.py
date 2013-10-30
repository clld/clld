from clld.web.util.helpers import JS
from clld.web.util.component import Component


class MultiSelect(Component):
    __template__ = 'clld:web/templates/multiselect.mako'

    def __init__(self, req, name, eid, collection=None, url=None, selected=None):
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
        return {'id': getattr(obj, 'id', obj.pk), 'text': '%s' % obj}

    def render(self, selected=None):
        if selected:
            self.selected = selected
        return Component.render(self)
