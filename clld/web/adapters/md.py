import datetime
from string import Template as StringTemplate

from zope.interface import implementer, implementedBy

from clld import interfaces
from clld.web.adapters.base import Representation
from clld.lib import bibtex


@implementer(interfaces.IRepresentation)
class BibTex(Representation):
    """Render a resource's metadata as BibTex record.
    """
    extension = 'bib'
    mimetype = 'text/x-bibtex'
    genre = 'incollection'

    def render(self, ctx, req):
        rec = bibtex.Record(
            self.genre,
            ctx.id,
            title=ctx.__unicode__(),
            url=req.resource_url(ctx),
            author=[c.name for c in
                    list(ctx.primary_contributors) + list(ctx.secondary_contributors)])
        return rec.__unicode__()


@implementer(interfaces.IRepresentation)
class TxtCitation(Representation):
    """Render a resource's metadata as plain text string.
    """
    extension = 'txt'
    mimetype = 'text/plain'

    def render(self, ctx, req):
        md = {'accessed': str(datetime.date.today())}
        if ctx:
            md.update(
                authors=', '.join(
                    c.name for c in
                    list(ctx.primary_contributors) + list(ctx.secondary_contributors)),
                title=getattr(ctx, 'citation_name', ctx.name),
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
        for key, value in req.registry.settings.items():
            if key.startswith('clld.publication.'):
                md[key.split('clld.publication.', 1)[1]] = value

        return template.safe_substitute(**md)
