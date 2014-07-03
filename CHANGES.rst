
Changes
-------

0.12.4
~~~~~~

Minor feature

* bootstrap-slider.js upgraded

Bugfixes

* fixed bug where volume would appear twice in linearization of bibtex record;
* fixed bug where selecting more than 4 parameters for combination would result in HTTP 500 rather than a warning.



0.12.3
~~~~~~

Minor feature

* allow zoom option for maps to be used as default zoom when used in combination with bounds.


0.12.2
~~~~~~

Bugfix release

* linearization of sources better aligned with unified stylesheet.


0.12.1
~~~~~~

Bugfix release:

* fixes a bug when EnumSymbols were compared with None.


0.12
~~~~

* Added GeoJson adapter for the case where a parameter may have multiple valuesets for the same language.
* Integrate results from searches on Internet Archive into source views.


0.11
~~~~

* Support serialization/deserialization of objects as rows in csv files.


0.10
~~~~

* Better support for RDF dumps.
* Support for deselcting languages in map view.


0.9
~~~

* Support for icon selection.
* Map configuration via URL parameters.
* Upgraded JqTree lib.


0.8.1
~~~~~

Enhanced test utilities.
Better docs.


0.8
~~~

Added support for common tasks in Alembic migration scripts.
Fixed a bug in the RDF serialization of parameters with domain.


0.7
~~~

Added support for range-operators when filtering DataTables on numeric columns.
Fixed a couple of bugs in the serializations of the RDF data.


0.6
~~~

New API to access registered maps using a method of the request object.


0.5.1
~~~~~

Bugfix release, fixing a critical js bug, where a reserved word was used as property name.


0.5
~~~

- New hook which allows using custom leaflet map markers with clld maps.
- Fixed bug where wrong order of inclusion of translation dirs would make customized
  translations impossible.


0.4
~~~

Resources have a new representation as JSON encoded documents suitable for
indexing with Solr.

