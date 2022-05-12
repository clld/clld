from markupsafe import Markup

from clld.interfaces import IDataTable
from clld.web.util.component import Component
from clld.web.util.htmllib import HTML, literal


class BaseToolbarWidget(Component):

    """Button group, grouping an info popover."""

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
            title: 'Column information',
            placement: '%s',
            trigger: 'click'
        });
    });""" % (self._opener_class, self.options['doc_position']))))

    def render(self, no_js=False):
        doc = HTML.div(self.doc())
        res = HTML.div(
            HTML.button(
                HTML.i(class_='icon-info-sign icon-white'),
                class_='btn btn-info %s' % self._opener_class,
                **{'data-content': str(doc), 'type': 'button'}))
        if no_js:
            return res
        return HTML.div(res, self.js())
