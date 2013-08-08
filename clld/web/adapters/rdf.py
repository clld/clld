from zope.interface import implementer, implementedBy

from clld import interfaces
from clld.web.adapters.base import Representation, Index
from clld.lib.rdf import convert
from clld.util import xmlchars


class Rdf(Representation):
    rdflibname = None

    def render(self, ctx, req):
        return convert(
            xmlchars(super(Rdf, self).render(ctx, req)), 'xml', self.rdflibname)


class RdfIndex(Index):
    rdflibname = None

    def render(self, ctx, req):
        return convert(super(RdfIndex, self).render(ctx, req), 'xml', self.rdflibname)
