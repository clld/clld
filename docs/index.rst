.. clld documentation master file, created by
   sphinx-quickstart on Wed Mar  6 08:56:47 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Cross-Linguistic Linked Data
============================

The Project
-----------

The goal of the Cross-Linguistic Linked Data project (CLLD) is to help collecting the world's
language diversity heritage. This is to be facilitated by developing, providing and
maintaining interoperable data publication structures.

For more information refer to the `project's website at clld.org <http://clld.org>`_.


The ``clld`` framework
----------------------

Underlying all applications built within the project to publish datasets is the ``clld``
framework - a python package providing functionality to build and maintain CLLD apps.

Design
~~~~~~

The main challenge for the ``clld`` framework is to balance abstraction and concreteness.

The following goals directed the design:

- There must be a core database model, which allows for as much shared functionality as
  possible. In particular, publication of Linked Data and integration with services such
  as `OLAC <http://www.language-archives.org/>`_ must be implemented by the framework.
- Deployment of CLLD applications must be uniform and easy.
- User interfaces of applications for browsers must be fully customizable.
- It must be easy to re-implement legacy applications using the framework.

These constraints led to the following design decisions:

- Target Ubuntu 12.04 with postgresql 9.1 and python 2.7 (but keep an eye on python 3.x compatibility) as
  primary deployment platform.
- Use `sqlalchemy <http://sqlalchemy.org>`_ and it's implementation of
  `joined table inheritance <http://docs.sqlalchemy.org/en/latest/orm/inheritance.html#joined-table-inheritance>`_
  to provide a core database model that can easily be extended.
- Use the `pyramid framework <http://docs.pylonsproject.org/projects/pyramid/>`_ for its
  `extensible configuration mechanism <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/extconfig.html>`_
  and support of the
  `Zope component architecture (zca) <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/zca.html>`_.
- Use `zca <http://www.muthukadan.net/docs/zca.html>`_ for pluggable functionality.
- Allow UI customization via i18n and templates.


Overview
~~~~~~~~

``clld`` provides

- a common core database model :py:mod:`clld.db.models.common`,
- a `pyramid application scaffold <http://docs.pylonsproject.org/projects/pyramid/en/latest/glossary.html#term-scaffold>`_,
- a core web application implemmented in the pyramid framework :py:mod:`clld.web.app`,
- scripts exploiting the core database model,
- deployment tasks implemented using fabric,
- libraries for common problems when working with linguistic databases.

Online documentation: http://clld.readthedocs.org/

Source code and issue tracker: https://github.com/clld/clld


Contents:

.. toctree::
    :maxdepth: 2

    tutorial
    resources
    datamodeling
    extending
    interfaces
    db
    web
    lib
    linkeddata
    protocols
    deployment
    trees


The applications
----------------

For a list of applications developed on top the ``clld`` framework see the
`list of CLLD datasets <http://clld.org/datasets>`_.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
