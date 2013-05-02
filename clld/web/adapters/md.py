import datetime
from string import Template as StringTemplate

from zope.interface import implementer, implementedBy

from clld import interfaces
from clld.web.adapters.base import Representation
from clld.lib import bibtex


class Metadata(Representation):
    @property
    def unapi_name(self):
        return getattr(self, 'unapi', self.extension)


#
# TODO: refactor! distinguish BibTexContribution and BibTexSite
#
@implementer(interfaces.IRepresentation, interfaces.IMetadata)
class BibTex(Metadata):
    """Render a resource's metadata as BibTex record.
    """
    unapi = 'bibtex'
    extension = 'md.bib'
    mimetype = 'text/x-bibtex'
    genre = 'incollection'

    def rec(self, ctx, req):
        return bibtex.Record(
            self.genre,
            ctx.id,
            title=getattr(ctx, 'citation_name', ctx.__unicode__()),
            url=req.resource_url(ctx),
            author=' and '.join([
                c.name for c in
                list(ctx.primary_contributors) + list(ctx.secondary_contributors)]),
            editor=req.pub.get('editors', ''),
            booktitle=req.pub.get('sitetitle', ''),
            address=req.pub.get('place', ''),
            publisher=req.pub.get('publisher', ''),
            year=req.pub.get('year', ''),
        )

    def render(self, ctx, req):
        return self.rec(ctx, req).__unicode__()


@implementer(interfaces.IRepresentation, interfaces.IMetadata)
class TxtCitation(Metadata):
    """Render a resource's metadata as plain text string.
    """
    extension = 'md.txt'
    mimetype = 'text/plain'

    def render(self, ctx, req):
        md = {'accessed': str(datetime.date.today())}
        if ctx:
            md.update(
                authors=', '.join(
                    c.name for c in
                    list(ctx.primary_contributors) + list(ctx.secondary_contributors)),
                title=getattr(ctx, 'citation_name', ctx.__unicode__()),
                path=req.resource_path(ctx))
            template = StringTemplate(md.get('template', """\
$authors. $year. $title.
In: $editors (eds.)
$sitetitle.
$place: $publisher.
(Available online at http://$domain$path, Accessed on $accessed.)
"""))
        else:
            md['path'] = '/'
            template = StringTemplate(md.get('template', """\
$editors (eds.) $year.
$sitetitle.
$place: $publisher.
(Available online at http://$domain$path, Accessed on $accessed.)
"""))
        md.update(req.pub)
        return template.safe_substitute(**md)
