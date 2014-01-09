# coding: utf8
from __future__ import unicode_literals

from paginate import Page

from clld.web.util.component import Component


class Pager(Component):
    """A pager component based on paginate.Page.
    """
    def __init__(self, req, collection, **kw):
        self.req = req
        self.page = Page(collection, **kw)

    def render(self):
        html = self.page.pager(
            format='<div class="pagination"><ul><li>~3~</li></ul></div>',
            separator='</li><li>',
            curpage_attr={'class': 'active'},
            dotdot_attr={'class': 'disabled'})
        return html\
            .replace('<span ', '<a ')\
            .replace('</span>', '</a>')\
            .replace('<li><a class="active"', '<li class="active"><a')\
            .replace('<li><a class="disabled"', '<li class="disabled"><a')
