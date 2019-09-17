from sqlalchemy import func, Index


def tsvector(obj):  # pragma: no cover
    return func.to_tsvector('english', '{0}'.format(obj))


def index(name, col, bind):  # pragma: no cover
    Index(name, col, postgresql_using='gin').create(bind)


def search(col, qs):  # pragma: no cover
    # https://bitbucket.org/zzzeek/sqlalchemy/issues/3160/postgresql-to_tsquery-docs-and
    query = func.plainto_tsquery('english', qs)
    return col.op('@@')(query)
