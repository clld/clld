from __future__ import unicode_literals, print_function, division, absolute_import

from six import string_types
from sqlalchemy import Column, Unicode

from clld.db.meta import Base, DBSession

__all__ = ('Config',)


class Config(Base):

    """Model class to allow storage of key-value pairs of configuration data.

    This model is also (ab-)used to implement a mechanism linking database
    objects of all types without enforcing referential intagrity, e.g. to model chains
    of superseding objects, where referred objects may become obsolete themselves.
    """

    key = Column(Unicode)
    value = Column(Unicode)

    gone = '__gone__'

    @staticmethod
    def replacement_key(model, id_):
        """Determine the replacement key for an object.

        :param model: Model class or instance.
        :param id_: Identifier of a class instance.
        :return: ``str`` representation identifying a database object.
        """
        if isinstance(model, string_types):
            name = model
        elif isinstance(model, type):
            name = model.__name__
        else:
            name = model.__class__.__name__
        return '__%s_%s__' % (name, id_)

    @classmethod
    def get_replacement_id(cls, model, id_):
        """Lookup and retrieve the ID of an object.

        :return: id of a resource registered as replacement for the specified resource.
        """
        res = DBSession.query(cls.value)\
            .filter(cls.key == cls.replacement_key(model, id_)).first()
        if res:
            return res[0]

    @classmethod
    def add_replacement(cls, replaced, replacement, model=None, session=None):
        """Method to register a replacement relation.

        :param replaced: db object or identifier of the object to be replaced.
        :param replacement: db object or identifier of the superseding object.
        :param model: If only an identifier is passed as ``replaced`` or ``replacement``\
        the corresponding model class must be passed as ``model``.
        :param session: Db session the relation is added to.
        """
        session = session or DBSession
        value = getattr(replacement, 'id', replacement) if replacement else cls.gone
        session.add(cls(
            key=cls.replacement_key(model or replaced, getattr(replaced, 'id', replaced)),
            value=value))
