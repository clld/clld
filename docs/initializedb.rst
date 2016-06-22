.. _initializedb:

Populating the database of a ``clld`` app
-----------------------------------------

In the following we will show how to create instances of all core model classes, thus
populating the database of a ``clld`` app. The code snippets should be understood as
living inside the ``main`` function of an app's ``scripts.initializedb`` module.


Metadata
~~~~~~~~

.. code-block:: python

    data = Data()

    dataset = common.Dataset(id=myapp.__name__, domain='myapp.clld.org')
    DBSession.add(dataset)

    # All ValueSets must be related to a contribution:
    contrib = common.Contribution(id='contrib', name='the contribution')

    # All ValueSets must be related to a Language:
    data.add(common.Language, 'eng', id='eng', name='English', latitude=52.0, longitude=0.0)
    data.add(common.Language, 'abk', id='abk', name='Abkhaz', latitude=43.08, longitude=41.0)


.. note::

    We use a :py:class:`clld.scripts.util.Data` instance and its ``add`` method to create
    objects we want to reference lateron.


Language-level parameters and values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Structural databases like WALS are best modeled using :py:class:`clld.db.models.common.Parameter`
objects for structural features and :py:class:`clld.db.models.common.Value` objects for
a single value assignment. So code to add WALS-like data could look as follows:

.. code-block:: python

    feature1 = common.Parameter(id='1A', name='Consonant Inventories')

    # ValueSets group Values related to the same Language, Contribution and Parameter
    vs = common.ValueSet(id='1A-eng', language=data['Language']['eng'], parameter=feature1, contribution=contrib)

    # Values store the actual "measurements":
    DBSession.add(common.Value(id='1A-eng', name='Average', valueset=vs))

Parameters often allow only values from a fixed domain. This can be modeled using
:py:class:`clld.db.models.common.DomainElement` objects:

.. code-block:: python

    feature2 = common.Parameter(id='9A', name='The velar nasal')

    # We add a DomainElement for Paramter feature2 ...
    no_velar_nasal = common.DomainElement(id='9A-1', name='No velar nasal', parameter=feature2)

    vs = common.ValueSet(id='1A-abk', language=data['Language']['abk'], parameter=feature2, contribution=contrib)

    # ... and reference this DomainElement when creating a Value:
    DBSession.add(common.Value(id='1A-abk', valueset=vs, domainelement=no_velar_nasal))


Unit-level parameters and values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Lexical databases typically provide information on words or lexemes. This kind of
data can be modeled using :py:class:`clld.db.models.common.Unit` and
:py:class:`clld.db.models.common.UnitParameter` objects.

.. code-block:: python

    # We model words as units of a language:
    unit = common.Unit(id='unit', name='hand', language=data['Language']['eng'])

    # Part of speech is a typical parameter which can be "measured" for words or lexemes.
    pos = common.UnitParameter(id='pos', name='part of speech')

    DBSession.add(common.UnitValue(id='unit-pos', name='noun', unit=unit, unitparameter=pos, contribution=contrib))

.. note::

    We could have used :py:class:`clld.db.models.common.UnitDomainElement` objects to model
    a controlled list of valid part-of-speech values.
