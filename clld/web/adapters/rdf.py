from zope.interface import implementer, implementedBy

from clld import interfaces
from clld.web.adapters.base import Representation
from clld.lib.rdf import convert


class Rdf(Representation):
    rdflibname = None

    def render(self, ctx, req):
        return convert(super(Rdf, self).render(ctx, req), 'xml', self.rdflibname)
