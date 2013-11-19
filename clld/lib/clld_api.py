from __future__ import unicode_literals
import re

import requests
from purl import URL

from clld.deploy import config


APPS = {}

for k, v in config.APPS.items():
    if getattr(v, 'domain', None):
        APPS[re.sub('[0-9]+', '', k)] = v.domain


def url(app, path='/', **query):
    u = URL(host=APPS[app], path=path, query=query)
    return u.query_params(query)


def json(app, **kw):
    try:
        return requests.get(url(app, **kw)).json()
    except:
        print url(app, **kw)
        raise


def resourcemap(app, type_):
    return json(app, path='/resourcemap.json', rsc=type_)
