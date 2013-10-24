from markupsafe import Markup
from pyramid.renderers import render

from clld.util import cached_property


class Component(object):
    __template__ = None

    @cached_property()
    def options(self):
        opts = self.get_default_options()
        opts.update(self.get_options() or {})
        return opts

    def render(self):
        return Markup(render(
            self.__template__, {'obj': self}, request=getattr(self, 'req', None)))

    def get_options(self):
        return {}

    def get_default_options(self):
        return {}
