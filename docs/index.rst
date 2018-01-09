.. clld documentation master file, created by
   sphinx-quickstart on Wed Mar  6 08:56:47 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Cross-Linguistic Linked Data
============================

The Project
-----------

The goal of the Cross-Linguistic Linked Data project (CLLD) is to help record the world's
language diversity heritage. This is to be facilitated by developing, providing and
maintaining interoperable data publication structures.

For more information refer to the `project's website at clld.org <http://clld.org>`_.


The ``clld`` framework
----------------------

Underlying all applications built within the project to publish datasets is the ``clld``
framework - a `python package <https://pypi.python.org/pypi/clld/>`_ providing functionality
to build and maintain CLLD apps.


Overview
~~~~~~~~

``clld`` provides

- a common core database model :py:mod:`clld.db.models.common`,
- a `pyramid application scaffold <http://docs.pylonsproject.org/projects/pyramid/en/latest/glossary.html#term-scaffold>`_,
- a core web application implemented in the pyramid framework :py:mod:`clld.web.app`,
- scripts exploiting the core database model,
- libraries for common problems when working with linguistic databases.

Online documentation is at `readthedocs <http://clld.readthedocs.org/>`_,
source code and issue tracker at `GitHub <https://github.com/clld/clld>`_.


Contents:

.. toctree::
    :maxdepth: 2

    tutorial
    initializedb
    resources
    datamodeling
    extending
    interfaces
    db
    web
    lib
    linkeddata
    protocols
    tools
    trees
    advanced
    design


The applications
----------------

For examples of applications developed on top of the ``clld`` framework see the
`list of CLLD datasets <http://clld.org/datasets.html>`_.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
