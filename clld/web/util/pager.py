# coding: utf8
"""Functionality to format HTML pagination controls."""
from __future__ import unicode_literals

from paginate import Page

from clld.web.util.component import Component


class Pager(Component):

    """A pager component based on paginate.Page.

    >>> pager = Pager(None, range(100), page=4, url_maker=lambda p: 'page %s' % p)
    >>> assert pager.render()
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
