"""Functionality to access the API of clld apps."""
from __future__ import unicode_literals

import requests
from purl import URL


#
# The following code implements functionality to retrieve an CLLD apps resource map.
# It may be used by CrossGram at some point.
#
def url(app, path='/', **query):
    u = URL(host=app, path=path, query=query)
    return str(u.query_params(query))


def json(app, **kw):
    return requests.get(url(app, **kw)).json()


def resourcemap(app, type_):
    """Retrieve the resource map oa an app.

    :param app: the domain or host of a CLLD app.
    """
    return json(app, path='/resourcemap.json', rsc=type_)
