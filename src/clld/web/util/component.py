"""Implementation of a component concept."""
from markupsafe import Markup
from pyramid.renderers import render
from clldutils.misc import cached_property


class Component(object):

    """Virtual base class for page components.

    Components are objects that can be rendered as HTML
    and typically define behavior using a corresponding JavaScript object which accepts
    an options object upon initialization.
    """

    __template__ = None

    @cached_property()
    def options(self):
        """Typically options to configure a corresponding JavaScript object.

        :return: JSON serializable dict
        """
        opts = self.get_default_options()
        opts.update(self.get_options() or {})
        opts.update(self.get_options_from_req() or {})
        return opts

    def render(self):
        return Markup(render(
            self.__template__, {'obj': self}, request=getattr(self, 'req', None)))

    def get_options(self):
        """Override this method to define final-class-specific options.

        :return: JSON serializable dict
        """
        return {}

    def get_default_options(self):
        """Override this method to define default (i.e. valid across subclasses) options.

        :return: JSON serializable dict
        """
        return {}

    def get_options_from_req(self):
        """Override this method to define options derived from request properties.

        :return: JSON serializable dict
        """
        return {}
