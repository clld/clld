"""
python postgres2sqlite.py apics 2>&1 >/dev/null | less
"""
from subprocess import call
from importlib import import_module
import pkg_resources
import re

from sqlalchemy import create_engine

from clld.db.meta import Base


def replace_booleans(line):
    """replaces postgres boolean literals with 0|1 within the values in an INSERT
    statement as created by pg_dump.

    .. note::

        - we rely on the INSERT statements not containing newlines.
        - we somewhat naively split the values at commas and assume that if a single
          token equals "true" or false", it was a boolean value in postgres. Obviously
          this assumption does not hold for a text value like "..., true, ...".
          We may switch to using sqlparse for a more robust detection of booleans.
    """
    insert, values = line.split('(', 1)
    assert values.endswith(');')
    values = values[:-2]
    clean_values = []
    for token in values.split(', '):
        if token == 'true':
            token = "1"
        elif token == 'false':
            token = "0"
        clean_values.append(token)
    return '%s(%s);\n' % (insert, ', '.join(clean_values))


STMT_END = re.compile("([^\']\'|\, [0-9]+)\)\;$")


def inserts(iterator):
    insert = []
    for line in iterator:
        line = line.strip()
        if line.startswith('INSERT '):
            if STMT_END.search(line):
                yield line
            else:
                insert = [line]
        else:
            if insert:
                # a continuation line!
                insert.append(line)
                if STMT_END.search(line):
                    c = '__newline__'.join(insert)
                    insert = []
                    yield c


def convert_dump(i, o):
    _insert = False
    with file(o, 'w') as fp:
        fp.write('.echo OFF\n.bail ON\n')
        fp.write('BEGIN;\n')
        for n, insert in enumerate(inserts(file(i))):
            fp.write(replace_booleans(insert))
        fp.write('END;\n')


def postgres2sqlite(name):
    call("pg_dump  -f /tmp/pg_{0}.sql --data-only --inserts {0}".format(name), shell=True)
    convert_dump('/tmp/pg_{0}.sql'.format(name), '/tmp/sqlite_{0}.sql'.format(name))
    engine = create_engine('sqlite:///{0}.sqlite'.format(name))
    m = import_module('{0}.models'.format(name))
    Base.metadata.create_all(engine)
    call('sqlite3 -bail -init /tmp/sqlite_{0}.sql {0}.sqlite ".exit"'.format(name), shell=True)


if __name__ == '__main__':
    import sys
    postgres2sqlite(sys.argv[1])
    sys.exit(0)
