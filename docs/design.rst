
Design
~~~~~~

The main challenge for the ``clld`` framework is to balance abstraction and concreteness.

The following goals directed the design:

- There must be a core database model, which allows for as much shared functionality as
  possible. In particular, publication of Linked Data and integration with services such
  as `OLAC <http://www.language-archives.org/>`_ must be implemented by the framework.
- Deployment of ``clld`` applications must be uniform and easy.
- User interfaces of applications for browsers must be fully customizable.
- It must be easy to re-implement legacy applications using the framework.

These constraints led to the following design decisions:

- Use `sqlalchemy <http://sqlalchemy.org>`_ and it's implementation of
  `joined table inheritance <http://docs.sqlalchemy.org/en/latest/orm/inheritance.html#joined-table-inheritance>`_
  to provide a core database model that can easily be extended.
- Use the `pyramid framework <http://docs.pylonsproject.org/projects/pyramid/>`_ for its
  `extensible configuration mechanism <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/extconfig.html>`_
  and support of the
  `Zope component architecture (zca) <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/zca.html>`_.
- Use `zca <http://www.muthukadan.net/docs/zca.html>`_ for pluggable functionality.
- Allow UI customization via i18n and overrideable templates.
