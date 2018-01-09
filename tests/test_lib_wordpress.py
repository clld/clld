# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from clld.lib.wordpress import *


def _requests(mocker, c, status=200):
    return mocker.Mock(get=lambda *a, **kw: mocker.Mock(text=c, status_code=status))


def test_sluggify():
    assert sluggify('a  and B') == 'a-and-b'


def test_Client(mocker):
    client = Client('blog.example.org', 'user', 'password')

    mocker.patch('clld.lib.wordpress.requests', _requests(mocker, '', status=404))
    client.get_post_id_from_path('/post')

    mocker.patch('clld.lib.wordpress.requests', _requests(mocker, '<div class="post" id="post-1">'))
    client.get_post_id_from_path('/post')

    mocker.patch(
        'clld.lib.wordpress.requests',
        _requests(mocker, '<input type="hidden" name="comment_post_ID" value="1" />'))
    client.get_post_id_from_path('/post')

    client.server = mocker.MagicMock()
    client.set_categories([{'name': 'cat', 'description': 'desc'}])
    client.set_categories([{'name': 'cat', 'description': 'desc'}], post_id=3)
    client.create_post(
        'title', 'content',
        date=1,
        tags=['tag'],
        custom_fields={'a': 'x'},
        categories=[{'name': 'cat', 'description': 'desc'}])

    client.server = mocker.MagicMock(wp=mocker.Mock(getCategories=mocker.Mock(return_value=[{
        'categoryName': 'n', 'categoryId': '1'}])))
    client.get_categories()
    client.get_categories(name='n')
    client.set_categories([{'name': 'n', 'description': 'desc'}])
