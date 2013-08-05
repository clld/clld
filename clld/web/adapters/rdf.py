from zope.interface import implementer, implementedBy

from clld import interfaces
from clld.web.adapters.base import Representation
from clld.lib.rdf import convert
from clld.util import xmlchars


class Rdf(Representation):
    rdflibname = None

    def render(self, ctx, req):
        return convert(
            xmlchars(super(Rdf, self).render(ctx, req)), 'xml', self.rdflibname)
