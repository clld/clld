
Data modeling
-------------

This chapter describes how to model cross-linguistic data using the core resources
available in the ``clld`` framework. While it is possible to extend the core data model
in various ways, sticking to core resources for comparable concepts will ensure
re-usability of the data, because all of the data publication mechanisms implemented
in ``clld`` will be available.


Dataset
~~~~~~~

Each ``clld`` app is assumed to serve a cross-linguistic dataset. The
:py:class:`clld.db.models.common.Dataset` object holds metadata about the dataset, e.g.
the publisher and license and relations to editors.


Languages
~~~~~~~~~

Languages are the core objects which are described in datasets served by ``clld`` apps.
:py:class:`clld.db.models.common.Language` - like most other objects - are at the most
basic level described by a name, an optional description and an optional geographical
coordinate.

To allow identification of languages across apps or even domains, languages can be
associated with any number of alternative
:py:class:`clld.db.models.common.Identifier`; typically glottocodes or iso 639-3
codes or alternative names.


Parameters
~~~~~~~~~~

:py:class:`clld.db.models.common.Parameter` objects are used to model language parameters,
i.e. phenomena (aka features) which can be measured across languages. Single datapoints,
i.e. measurements of the parameter for a single language are modeled as instances of
:py:class:`clld.db.models.common.Value`. To support multiple measurements for the same
(language, parameter) pair, values are grouped in a
:py:class:`clld.db.models.common.ValueSet`, and it is the valueset that is related to
language and parameter.

Enumerated domain
+++++++++++++++++

``clld`` supports enumerated domains. Elements of the domain of a parameter can be modeled
as :py:class:`clld.db.models.common.DomainElement` instances and each value must then be
related to one domain element.

The ``clld`` framework will then use the ``domain`` property of a parameter to select
behaviour suitable for enumerated domains only, e.g. loading values associated with one
domain element as separate layer when displaying a parameter map.


Typed values
++++++++++++

The ``clld`` framework is agnostic with regard to the types of values, i.e. as far as
default functionality is concerned the only properties required of a value are a ``name``
and an ``id`` (and optionally a ``description``). To simply store typed data for values
multiple mechanisms are available.

- Storing typed data in the ``jsondata`` dictionary: This accomodates all data types
  which can be serialized as JSON, i.e. numbers, booleans, arrays, dictionaries.
- If the data for a value comes as a list or dictionary of strings, it can also be stored
  as :py:class:`clld.db.models.common.Value_data` instances.
- Finally there's the option to store data related to a value as files, i.e. as instances
  of :py:class:`clld.db.models.common.Value_files`.
