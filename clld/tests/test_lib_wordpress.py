# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from mock import Mock, MagicMock, patch


class Tests(unittest.TestCase):
    def _requests(self, c, status=200):
        return Mock(get=lambda *a, **kw: Mock(text=c, status_code=status))

    def test_sluggify(self):
        from clld.lib.wordpress import sluggify

        assert sluggify('a  and B') == 'a-and-b'

    def test_Client(self):
        from clld.lib.wordpress import Client

        client = Client('blog.example.org', 'user', 'password')

        with patch('clld.lib.wordpress.requests',
                   self._requests('', status=404)):
            client.get_post_id_from_path('/post')

        with patch('clld.lib.wordpress.requests',
                   self._requests('<div class="post" id="post-1">')):
            client.get_post_id_from_path('/post')

        with patch('clld.lib.wordpress.requests',
                   self._requests('<input type="hidden" name="comment_post_ID" value="1" '
                                  '/>')):
            client.get_post_id_from_path('/post')

        client.server = MagicMock()
        client.set_categories([{'name': 'cat', 'description': 'desc'}])
        client.set_categories([{'name': 'cat', 'description': 'desc'}], post_id=3)
        client.create_post(
            'title', 'content',
            date=1,
            tags=['tag'],
            custom_fields={'a': 'x'},
            categories=[{'name': 'cat', 'description': 'desc'}])

        client.server = MagicMock(wp=Mock(getCategories=Mock(return_value=[{
            'categoryName': 'n', 'categoryId': '1'}])))
        client.get_categories()
        client.get_categories(name='n')
        client.set_categories([{'name': 'n', 'description': 'desc'}])
