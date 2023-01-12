"""Adapters to serialize metadata of clld objects."""
import itertools

from zope.interface import implementer

from clld import interfaces
from clld.web.adapters.base import Representation
from clld.lib import bibtex
from clld.web.util import doi


class Metadata(Representation):

    """Virtual base class."""

    rel = 'describedby'

    @property
    def unapi_name(self):
        return getattr(self, 'unapi', self.extension)


class MetadataFromRec(Metadata):

    """Virtual base class deriving metadata from a bibtex record."""

    def rec(self, ctx, req):
        zdoi = req.registry.settings.get('clld.zenodo_version_doi') or \
            req.registry.settings.get('clld.zenodo_concept_doi')
        data = {}
        if zdoi:
            data.update(doi=zdoi, type='Data set', url=doi.url(zdoi), publisher='Zenodo')
        else:
            data.update(
                url=req.resource_url(ctx),
                address=req.dataset.publisher_place,
                publisher=req.dataset.publisher_name)

        if interfaces.IContribution.providedBy(ctx):
            genre = 'incollection'
            data['author'] = [
                c.name for c in
                itertools.chain(ctx.primary_contributors, ctx.secondary_contributors)]
            data['booktitle'] = req.dataset.description
            data['editor'] = [c.contributor.name for c in req.dataset.editors]
            id_ = '%s-%s' % (req.dataset.id, ctx.id)
        else:
            genre = 'book'
            data['editor'] = [c.contributor.name for c in ctx.editors]
            id_ = req.dataset.id

        return bibtex.Record(
            genre,
            id_,
            title='{}{}'.format(
                getattr(ctx, 'citation_name', str(ctx)),
                (' ({})'.format(req.registry.settings['clld.zenodo_version_tag'])
                 if req.registry.settings.get('clld.zenodo_version_doi') else ''),
            ),
            year=str(req.dataset.published.year),
            **data)


@implementer(interfaces.IRepresentation, interfaces.IMetadata)
class BibTex(MetadataFromRec):

    """Resource metadata as BibTex record."""

    name = 'BibTeX'
    __label__ = 'BibTeX'
    unapi = 'bibtex'
    extension = 'md.bib'
    mimetype = 'text/x-bibtex'

    def render(self, ctx, req):
        return str(self.rec(ctx, req))


@implementer(interfaces.IRepresentation, interfaces.IMetadata)
class TxtCitation(Metadata):

    """Resource metadata formatted as plain text citation."""

    name = "Citation"
    __label__ = 'Text'
    extension = 'md.txt'
    mimetype = 'text/plain'

    def render(self, ctx, req):
        if interfaces.IContribution.providedBy(ctx):
            self.template = 'contribution/md_txt.mako'
        else:  # if interfaces.IDataset.providedBy(ctx):
            self.template = 'dataset/md_txt.mako'
        return super(TxtCitation, self).render(ctx, req)
