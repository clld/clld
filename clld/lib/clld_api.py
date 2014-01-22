from __future__ import unicode_literals

import requests
from purl import URL


#
# The following code implements functionality to retrieve an CLLD apps resource map.
# It may be used by CrossGram at some point.
#
def url(app, path='/', **query):  # pragma: no cover
    u = URL(host=app, path=path, query=query)
    return str(u.query_params(query))


def json(app, **kw):  # pragma: no cover
    return requests.get(url(app, **kw)).json()


def resourcemap(app, type_):  # pragma: no cover
    """
    :param app: the domain or host of a CLLD app.
    """
    return json(app, path='/resourcemap.json', rsc=type_)
