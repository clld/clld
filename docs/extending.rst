
Customizing a CLLD app
----------------------

Extending or customizing the default behaviour of a CLLD app is basically what pyramid
calls `configuration <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/configuration.html>`_.
So, since the ``clld_app`` scaffold is somewhat tuned towards imperative configuration,
this means calling methods on the config object returned by the call to
:py:func:`clld.web.app.get_configurator` in the apps ``main`` function.
Since the config object is an instance of the pyramid
`Configurator <http://docs.pylonsproject.org/projects/pyramid/en/latest/api/config.html#pyramid.config.Configurator>`_
this includes all the standard ways to configure pyramid apps, in particular adding
routes and views to provide additional pages and funtionality with an app.


Wording
~~~~~~~

Most text displayed on the HTML pages of the default app can be customized using a technique
commonly called `localization <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/i18n.html>`_.
I.e. the default is set up in an "internationalized" way, which can be "localized" by providing
alternative "translations".

These translations are provided in form of a `PO file <http://www.gnu.org/software/gettext/manual/html_node/PO-Files.html>`_
which can be edited by hand or with tools such as `Poedit <http://www.poedit.net>`_.

The workflow to create alternative translations for core terms of a CLLD app is as follows:

1. Look up the terms available for translation in ``clld/locale/en/LC_MESSAGES/clld.po``.
   If the term you want to translate is found, go on. Otherwise file an issue at https://github.com/clld/clld/issues
2. Initialize a localized catalog for your app running::

    python setup.py init_catalog -l en

3. When installing ``clld`` tools have been installed to
   `extract terms from python code files <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/i18n.html#extracting-messages-from-code-and-templates>`_.
   To make the term available for extraction, include code like below in ``myapp``.

.. code-block:: python

    # _ is a recognized name for a function to mark translatable strings
    _ = lambda s: s
    _('term you wish to translate')

4. Extract terms from your code and update the local ``myapp/locale/en/LC_MESSAGES/clld.po``::

    python setup.py extract_messages
    python setup.py update_catalog

5. Add a translation by editing ``myapp/locale/en/LC_MESSAGES/clld.po``.
6. Compile the catalog::

    python setup.py compile_catalog

If you restart your app you should see your translation at places where previously the core term appeared.
Whenever you want to add translations, you have to go through steps 3--6 above.


Static Pages
~~~~~~~~~~~~

TODO: reserved route names, ...


Templates
~~~~~~~~~

The default CLLD app comes with a set of `Mako templates <http://makotemplates.org>`_
(in ``clld/web/templates``) which control the rendering of HTML pages. Each of these can be
overridden locally by providing a template file with the same path (relative to the ``templates``
directory); i.e. to override ``clld/web/templates/language/detail_html.mako`` -- the template
rendered for the details page of languages (see :ref:`sec-resource-templates`) -- you'd have to provide a file
``myapp/templates/language/detail_html.mako``.


Static assets
~~~~~~~~~~~~~

CLLD Apps may provide custom css and js code. If this code is placed in the default
locations ``myapp/static/project.[css|js]``, it will automatically be packaged for
production. Note that in this case the code should not contain any URLs relative to
the file, because these may break in production.

Other static content can still be placed in the ``myapp/static`` directory but must be
explicitely included on pages making use of it, e.g. with template code like:

.. code-block:: html

    <link href="${request.static_url('myapp:static/css/introjs.min.css')}" rel="stylesheet">
    <script src="${request.static_url('myapp:static/js/intro.min.js')}"></script>


Menu Items
~~~~~~~~~~

Registering non-default menu items can only be done wholesale, i.e. replacing the whole
main menu by calling the ``register_menu`` method of the config object.

.. py:function:: register_menu(*items) #*

    :param items: (name, factory) pairs, where factory is a callable that accepts the two parameters (ctx, req) and returns a pair (url, label) to use for the menu link and name is used to compare with the ``active_menu`` attribute of templates.


Datatables
~~~~~~~~~~

A main building block of CLLD apps are dynamic data tables. Although there are default
implementations which may be good enough in many cases, each data table can be fully
customized as follows.

1. Define a customized datatable class in ``myapp/datables.py`` inheriting from either
:py:class:`clld.web.datatables.base.DataTable` or one
of its subclasses in :py:mod:`clld.web.datatables`.

2. Register this datatable for the page you want to display it on by
adding a line like the following to the function ``myapp.datatables.includeme``::

    config.register_datatable('routename', DataTableClassName)

The ``register_datatable`` method of the config object has the following signature:

.. py:function:: register_datatable(route_name, cls)

    :param str route_name: Name of the route which maps to the view serving the page (see :ref:`sec-resource-routes`).
    :param class cld: Python class inheriting from :py:class:`clld.web.datatables.base.DataTable`.


Customize column definitions
++++++++++++++++++++++++++++

Overwrite :py:meth:`clld.web.datatables.base.DataTable.col_defs`.


Customize query
++++++++++++++++

Overwrite :py:meth:`clld.web.datatables.base.DataTable.base_query`.


Data model
~~~~~~~~~~

The core ``clld`` data model can be extended for CLLD apps by defining additional
`mappings <http://docs.sqlalchemy.org/en/rel_0_9/orm/tutorial.html#declare-a-mapping>`_
in ``myapp.models`` in two ways:

- Additional mappings (thus additional database tables) deriving from :py:class:`clld.db.meta.Base`
  can be defined.
- Customizations of core models can be defined using joined table inheritance:

.. code-block:: python
    :emphasize-lines: 7,8,12

    from sqlalchemy import Column, Integer, ForeignKey
    from zope.interface import implementer
    from clld.interfaces import IContribution
    from clld.db.meta import CustomModelMixin
    from clld.db.models.common import Contribution

    @implementer(IContribution)
    class Chapter(Contribution, CustomModelMixin):
        """Contributions in WALS are chapters chapters. These comprise a set of features with
        corresponding values and a descriptive text.
        """
        pk = Column(Integer, ForeignKey('contribution.pk'), primary_key=True)
        # add more Columns and relationships here


To give an example, here's how one could model the many-to-many relation between words and
meanings often encountered in lexical databases:

.. code-block:: python

    from clld import interfaces
    from clld.db.models import common
    from clld.db.meta import CustomModelMixin

    @implementer(interfaces.IParameter)
    class Meaning(common.Parameter, CustomModelMixin):
        pk = Column(Integer, ForeignKey('parameter.pk'), primary_key=True)

    @implementer(interfaces.IValueSet)
    class SynSet(common.ValueSet, CustomModelMixin):
        pk = Column(Integer, ForeignKey('valueset.pk'), primary_key=True)

    @implementer(interfaces.IUnit)
    class Word(common.Unit, CustomModelMixin):
        pk = Column(Integer, ForeignKey('unit.pk'), primary_key=True)

    @implementer(interfaces.IValue)
    class Counterpart(common.Value, CustomModelMixin):
        """a counterpart relates a meaning with a word
        """
        pk = Column(Integer, ForeignKey('value.pk'), primary_key=True)

        word_pk = Column(Integer, ForeignKey('unit.pk'))
        word = relationship(Word, backref='counterparts')

The definitions of ``Meaning``, ``Synset`` and ``Word`` above are not strictly necessary
(because they do not add any relations or columns to the base classes) and are only
added to make the semantics of the model clear.

Now if we have an instance of ``Word``, we can iterate over its meanings like this

.. code-block:: python

    for counterpart in word.counterparts:
        print counterpart.valueset.parameter.name

A more involved example for the case of tree-structured data is given in :doc:`trees`.


.. _sec-extending-resource:

Adding a resource
~~~~~~~~~~~~~~~~~

You may also want to add new resources in your app, i.e. objects that behave like builtin
resources in that routes get automatically registered and view and template lookup works
as explained in :ref:`sec-resource-request`.
An example for this technique are the families in e.g. `WALS <http://wals.info/languoid/family/khoisan>`_.

The steps required to add a custom resource are:

1. Define an interface for the resource in ``myapp/interfaces.py``:

.. code-block:: python

    from zope.interface import Interface

    class IFamily(Interface):
        """marker"""

2. Define a model in ``myapp/models.py``.

.. code-block:: python

    @implementer(myapp.interfaces.IFamily)
    class Family(Base, common.IdNameDescriptionMixin):
        pass

3. Register the resource in ``myapp.main``:

.. code-block:: python

    config.register_resource('family', Family, IFamily)

4. Create templates for HTML views, e.g. ``myapp/templates/family/detail_html.mako``,
5. and register these:

.. code-block:: python

    from clld.web.adapters.base import adapter_factory
    ...
    config.register_adapter(adapter_factory('family/detail_html.mako'), IFamily)


Custom maps
~~~~~~~~~~~

TODO


Custom URLs
~~~~~~~~~~~

When an established database is ported to CLLD it may be necessary to support legacy URLs
for its resources (as was the case for WALS). This can be achieved by passing a ``route_patterns``
dict, mapping route names to custom patterns, in the settings to :py:func:`clld.web.app.get_configurator`
like in the following example from WALS:

.. code-block:: python

    def main(global_config, **settings):
        settings['route_patterns'] = {
            'languages': '/languoid',
            'language': '/languoid/lect/wals_code_{id:[^/\.]+}',
        }
        config = get_configurator('wals3', **dict(settings=settings))


Downloads
~~~~~~~~~

TODO


Misc Utilities
~~~~~~~~~~~~~~

http://www.muthukadan.net/docs/zca.html#utility

- IMapMarker
- ILinkAttrs
- ICtxFactoryQuery
