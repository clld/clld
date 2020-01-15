"""Generic utility functions."""
import re
import random
import string
import pathlib
import contextlib

from sqlalchemy.types import SchemaType, TypeDecorator, Enum
from clldutils.path import move
from clldutils.declenum import DeclEnum as BaseEnum
from clldutils.lgr import ABBRS as LGR_ABBRS
assert LGR_ABBRS


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
    res = ''
    words = list(reversed(text.split()))
    while words:
        nextword = words.pop()
        if len(res) + len(nextword) + 1 > max_length:
            # too long, add the word back onto the remainder
            words.append(nextword)
            break
        res += ' ' + nextword
    if words:
        res += ' ...'
    return res.strip()


# From "The Enum Recipe": http://techspot.zzzeek.org/2011/01/14/the-enum-recipe/
class DeclEnum(BaseEnum):
    @classmethod
    def db_type(cls):
        return DeclEnumType(cls)


class DeclEnumType(SchemaType, TypeDecorator):
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
