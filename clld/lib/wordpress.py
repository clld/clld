"""
client for the xmlrpc API of a wordpress blog

.. note::

    we ignore blog_id altogether, see
    http://joseph.randomnetworks.com/archives/2008/06/10/\
    blog-id-in-wordpress-and-xml-rpc-blog-apis/
    thus, rely on identifying the appropriate blog by xmlrpc endpoint.
"""
import re
import xmlrpclib

import requests


XMLRPC_PATH = 'xmlrpc.php'


def sluggify(phrase):
    """
    >>> assert sluggify('a  and B') == 'a-and-b'
    """
    phrase = phrase.lower().strip()
    phrase = re.sub('\s+', '-', phrase)
    return phrase


class Client(object):
    """client to a wpmu blog

    provides a unified interface to functionality called over xmlrpc or plain http

    >>> c = Client('blog.example.org', 'user', 'password')
    >>> assert c.service_url == 'http://blog.example.org/xmlrpc.php'
    """
    def __init__(self, url, user, password):
        self.user = user
        self.password = password
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'http://' + url
        if not url.endswith(XMLRPC_PATH):
            if not url.endswith('/'):
                url += '/'
            url += XMLRPC_PATH
        self.service_url = url
        self.server = xmlrpclib.Server(self.service_url)
        self.base_url = self.service_url.replace(XMLRPC_PATH, '')

    def get_post(self, id):  # pragma: no cover
        return self.server.metaWeblog.getPost(id, self.user, self.password)

    def get_authors(self):  # pragma: no cover
        return self.server.wp.getAuthors(0, self.user, self.password)

    def get_recent_posts(self, number_of_posts):  # pragma: no cover
        return self.server.metaWeblog.getRecentPosts(
            0, self.user, self.password, number_of_posts)

    def create_post(self,
                    title,
                    content,
                    categories=None,
                    published=False,
                    date=None,
                    tags='',
                    custom_fields=None,
                    **kwargs):
        published = [xmlrpclib.False, xmlrpclib.True][int(published)]
        struct = dict(title=title, description=content)
        if date:
            struct['date_created_gmt'] = date
            struct['dateCreated'] = date
        if tags:
            if isinstance(tags, (list, tuple)):
                tags = ','.join(tags)
            struct['mt_keywords'] = tags
        if custom_fields is not None:
            struct['custom_fields'] = [
                dict(key=key, value=value) for key, value in custom_fields.items()]
        struct.update(kwargs)
        post_id = self.server.metaWeblog.newPost(
            '', self.user, self.password, struct, published)
        if categories:
            self.set_categories(categories, post_id)
        return post_id

    def get_categories(self, name=None):
        res = []
        for c in self.server.wp.getCategories('', self.user, self.password):
            if name:
                if c['categoryName'] == name:
                    res.append(c)
            else:
                res.append(c)
        for c in res:
            c['name'] = c['categoryName']
            c['id'] = c['categoryId']
        return res

    def set_categories(self, categories, post_id=None):
        existing_categories = dict(
            [(c['categoryName'], c) for c in self.get_categories()])
        cat_map = {}
        for cat in categories:
            if cat['name'] not in existing_categories:
                struct = dict(name=cat['name'])
                for attr in ['parent_id', 'description', 'slug']:
                    if attr in cat:
                        struct[attr] = cat[attr]
                cat_map[cat['name']] = int(
                    self.server.wp.newCategory('', self.user, self.password, struct))
            else:
                cat_map[cat['name']] = int(existing_categories[cat['name']]['id'])
        if post_id:
            self.server.mt.setPostCategories(
                post_id,
                self.user,
                self.password,
                [dict(categoryId=cat_map[name]) for name in cat_map])
        return cat_map

    def get_post_id_from_path(self, path):
        """
        pretty hacky way to determine whether some post exists
        """
        if not path.startswith(self.base_url):
            path = self.base_url + path
        res = requests.get(path)
        if res.status_code != 200:
            return None
        m = re.search(
            '\<input type\="hidden" name\="comment_post_ID" value\="(?P<id>[0-9]+)" \/\>',
            res.text)
        if m:
            return int(m.group('id'))
        else:
            p = '\<div\s+class\=\"post\"\s+id\=\"post\-(?P<id>[0-9]+)\"\>'
            if len(re.findall(p, res.text)) == 1:
                m = re.search(p, res.text)
                return int(m.group('id'))
