"""Generic utility functions."""
import re
import random
import string
import pathlib
import contextlib

from sqlalchemy.sql.sqltypes import SchemaType
from sqlalchemy.types import TypeDecorator, Enum
from clldutils.path import move
from clldutils.declenum import DeclEnum as BaseEnum
from clldutils.lgr import ABBRS as LGR_ABBRS
assert LGR_ABBRS

__all__ = ['random_string', 'safe_overwrite', 'summary', 'DeclEnum', 'DeclEnumType']


def random_string(length):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))


@contextlib.contextmanager
def safe_overwrite(fname):
    fname = pathlib.Path(fname)
    if not fname.parent.exists():
        fname.parent.mkdir()
    assert fname.parent.exists()
    tmp = fname.parent
    while tmp.exists():
        tmp = fname.parent.joinpath('%s.%s' % (fname.name, random_string(6)))
    yield tmp
    if fname.exists():
        fname.unlink()
    move(tmp, fname)


def summary(text, max_length=70):
    from textwrap import shorten
    if max_length < 4:
        return '...'
    return shorten(text, width=max_length, placeholder=' ...')


# From "The Enum Recipe": http://techspot.zzzeek.org/2011/01/14/the-enum-recipe/
class DeclEnum(BaseEnum):
    @classmethod
    def db_type(cls):
        return DeclEnumType(cls)


class DeclEnumType(SchemaType, TypeDecorator):
    cache_ok = True

    def __init__(self, enum):
        self.enum = enum
        self.impl = Enum(
            *enum.values(),
            name="ck%s" % re.sub(
                '([A-Z])', lambda m: "_" + m.group(1).lower(), enum.__name__))

    def _set_table(self, table, column):
        self.impl._set_table(table, column)  # pragma: no cover

    def copy(self):
        return DeclEnumType(self.enum)  # pragma: no cover

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return value.value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return self.enum.from_string(value.strip())
