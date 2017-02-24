# coding: utf8
from __future__ import unicode_literals, print_function, division

from sqlalchemy import func, Index


def tsvector(obj):  # pragma: no cover
    return func.to_tsvector('english', '{0}'.format(obj))


def index(name, col, bind):  # pragma: no cover
    Index(name, col, postgresql_using='gin').create(bind)


def search(col, qs):  # pragma: no cover
    qs = qs.replace('\\', '\\\\')
    return col.match('{0}'.format(' & '.join(qs.split())), postgresql_regconfig='english')
