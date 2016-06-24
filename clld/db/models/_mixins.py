from __future__ import unicode_literals, print_function, division, absolute_import

import os

from six import text_type
from sqlalchemy import Column, Integer, String, Unicode, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from clldutils.path import Path

__all__ = (
    'IdNameDescriptionMixin',
    'FilesMixin', 'HasFilesMixin',
    'DataMixin', 'HasDataMixin',
)


class IdNameDescriptionMixin(object):

    """Mixin for 'visible' objects, i.e. anything that has to be displayed.

    In particular all :doc:`resources` fall into this category.

    .. note::

        Only one of :py:attr:`clld.db.models.common.IdNameDescriptionMixin.description`
        or :py:attr:`clld.db.models.common.IdNameDescriptionMixin.markup_description`
        should be supplied, since these are used mutually exclusively.
    """

    id = Column(String, unique=True)
    """A ``str`` identifier of an object which can be used for sorting and as part of a
    URL path; thus should be limited to characters valid in URLs, and should not contain
    '.' or '/' since this may trip up route matching.
    """

    name = Column(Unicode)
    """A human readable 'identifier' of the object."""

    description = Column(Unicode)
    """A description of the object."""

    markup_description = Column(Unicode)
    """A description of the object containing HTML markup."""


# ----------------------------------------------------------------------------
# We augment mapper classes for basic objects using mixins to add the ability
# to store arbitrary key-value pairs and files associated with an object.
# ----------------------------------------------------------------------------
class FilesMixin(IdNameDescriptionMixin):

    """This mixin provides a way to associate files with instances of another model class.

    .. note::

        The file itself is not stored in the database but must be created in the
        filesystem, e.g. using the create method.
    """

    @classmethod
    def owner_class(cls):
        return cls.__name__.split('_')[0]

    ord = Column(Integer, default=1)
    """Ordinal to control sorting of files associated with one db object."""

    mime_type = Column(String)
    """Mime-type of the file content."""

    @declared_attr
    def object_pk(cls):
        return Column(Integer, ForeignKey('%s.pk' % cls.owner_class().lower()))

    @property
    def relpath(self):
        """OS file path of the file relative to the application's file-system dir."""
        return os.path.join(self.owner_class().lower(), str(self.object.id), str(self.id))

    def create(self, dir_, content):
        """Write ``content`` to a file using ``dir_`` as file-system directory.

        :return: File-system path of the file that was created.
        """
        p = Path(dir_).joinpath(self.relpath)
        if not p.parent.exists():
            p.parent.mkdir(parents=True)
        with open(p.as_posix(), 'wb') as fp:
            if isinstance(content, text_type):
                content = content.encode('utf8')
            fp.write(content)
        return p.as_posix()


class HasFilesMixin(object):

    """Mixin for model classes which may have associated files."""

    @property
    def files(self):
        """return ``dict`` of associated files keyed by ``id``."""
        return dict((f.id, f) for f in self._files)

    @declared_attr
    def _files(cls):
        return relationship(cls.__name__ + '_files', backref='object')


class DataMixin(object):

    """Provide a simple way to attach key-value pairs to a model class given by name."""

    @classmethod
    def owner_class(cls):
        return cls.__name__.split('_')[0]

    key = Column(Unicode)
    value = Column(Unicode)
    ord = Column(Integer, default=1)

    @declared_attr
    def object_pk(cls):
        return Column(Integer, ForeignKey('%s.pk' % cls.owner_class().lower()))


class HasDataMixin(object):

    """Adds a convenience method to retrieve the key-value pairs from data as dict.

    .. note::

        It is the responsibility of the programmer to make sure conversion to a ``dict``
        makes sense, i.e. the keys in data are actually unique, thus usable as dictionary
        keys.
    """

    def datadict(self):
        """return ``dict`` of associated key-value pairs."""
        return dict((d.key, d.value) for d in self.data)

    @declared_attr
    def data(cls):
        return relationship(cls.__name__ + '_data', order_by=cls.__name__ + '_data.ord')
