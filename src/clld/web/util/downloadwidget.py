from __future__ import unicode_literals

from six import text_type
from markupsafe import Markup

from clld.interfaces import IDataTable
from clld.web.util.component import Component
from clld.web.util.htmllib import HTML, literal


class DownloadWidget(Component):

    """Button group, grouping an info popover and a download selection."""

    def __init__(self, req, ctx, obj, dl_url_tmpl, interface, **kw):
        self.req = req
        self.ctx = ctx
        self.obj = obj
        self.dl_url_tmpl = dl_url_tmpl
        self.interface = interface
        kw.setdefault('doc_position', 'right')
        kw.setdefault('exclude', ['html', 'snippet.html'])
        self._kw = kw
        self._opener_class = 'dl-widget-%s' % self.interface.__name__
        self._id_prefix = 'dt-dl-' if IDataTable.providedBy(ctx) else 'rsc-dl-'

    def get_default_options(self):
        return self._kw

    def doc(self):
        """Override to supply additional information in the information popup.

        :return: HTML string.
        """
        return ''

    def js(self):
        return Markup(HTML.script(literal("""\
    $(document).ready(function() {
        $('.%s').clickover({
            html: true,
            title: 'Download information',
            placement: '%s',
            trigger: 'click'
        });
    });""" % (self._opener_class, self.options['doc_position']))))

    def dl_link(self, adapter):
        return HTML.a(
            adapter.name or adapter.extension,
            href="#",
            id=self._id_prefix + adapter.extension,
            onclick="document.location.href = %s; return false;"
                    % (self.dl_url_tmpl % adapter.extension))

    def render(self, no_js=False):
        adapters = [a for n, a in
                    self.req.registry.getAdapters([self.obj], self.interface)
                    if a.extension not in set(self.options['exclude'])]
        adapters = sorted(adapters, key=lambda x: x.extension)
        adoc = []
        for adapter in adapters:
            if adapter.__doc__:
                adoc.append(HTML.dt(adapter.name or adapter.extension))
                adoc.append(HTML.dd(adapter.__doc__))
        doc = HTML.div(
            HTML.p(
                """You may download alternative representations of the data on
"%s" by clicking the button """ % self.ctx,
                HTML.i(class_='icon-download-alt')),
            self.doc(),
            HTML.dl(*adoc))
        res = HTML.div(
            HTML.button(
                HTML.i(class_='icon-info-sign icon-white'),
                class_='btn btn-info %s' % self._opener_class,
                **{'data-content': text_type(doc), 'type': 'button'}),
            HTML.a(
                HTML.i(class_='icon-download-alt'),
                HTML.span(class_="caret"),
                **{
                    'class_': "btn dropdown-toggle",
                    'data-toggle': "dropdown",
                    'href': "#",
                    'id': self._id_prefix + "opener"}),
            HTML.ul(
                *[HTML.li(self.dl_link(adapter)) for adapter in adapters],
                **dict(class_="dropdown-menu")),
            class_='btn-group right')
        if no_js:
            return res
        return HTML.div(res, self.js())
