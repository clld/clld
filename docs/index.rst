.. clld documentation master file, created by
   sphinx-quickstart on Wed Mar  6 08:56:47 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Cross-Linguistic Linked Data
============================

The Project
-----------

The goal of Cross-Linguistic Linked Data project (CLLD) is to help collecting the world's
language diversity heritage. This is to be facilitated by developing, providing and
maintaining interoperable data publication structures.

These publication structures come in three kinds:

1. software, by providing `a framework for lexical/grammatical databases <https://github.com/clld/clld>`_,
2. organizational, by creating lexical/grammatical database journals,
3. infrastructural, by providing a `comprehensive language catalogue and bibliography <http://glottolog.org>`_.


The Software
------------

Design
~~~~~~

The main challenge for the CLLD framework is to balance abstraction and concreteness.

The following goals directed the design:

- There should be a core database model, which allows for as much shared functionality as
  possible. In particular, publication of Linked Data and integration with services such
  as `OLAC <http://www.language-archives.org/>`_ must be implemented by the framework.
- Deployment of CLLD applications must be uniform and easy.
- User interfaces of applications for browsers must be fully customizable.
- It must be easy to re-implement legacy applications using the framework.

These constraints led to the following design decisions:

- Target Ubuntu 12.04 with python 2.7 (but keep an eye on python 3.x compatibility) as
  primary deployment platform.
- Use sqlalchemy and it's implementation of joined table inheritance to provide a core
  database model that can easily be extended.
- Use the pyramid framework for its extensible configuration mechanism and support of the
  Zope component architecture (zca).
- Use zca for pluggable functionality.
- Allow UI customization via i18n and templates.


The clld package
~~~~~~~~~~~~~~~~

clld provides

- a common core database model,
- a pyramid application scaffold,
- a core web application implemmented in the pyramid framework,
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
    interfaces
    db
    web
    lib
    linkeddata
    protocols
    extending
    deployment


The applications
----------------

The following applications are developed on top the clld framework:

- `wals3 <https://github.com/clld/wals3>`_: The application that will serve http://wals.info
- `glottolog3 <https://github.com/clld/glottolog3>`_: The application serving http://glottolog.org



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
