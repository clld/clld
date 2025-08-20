
Changes
-------


11.4.0
~~~~~~

- Make more title attributes of HTML elements created from templates in util.mako available
  for translation.
- Fix issue whereby `Source` objects could not have arbitrary `jsondata` properties.


11.3.1
~~~~~~

Re-instate support for python 3.8 since it's still supported on Ubuntu 20.04 lts.


11.3.0
~~~~~~

- Support python 3.13.
- Drop support for python 3.8.


11.2.3
~~~~~~

- Addressed rendering issue with IGT examples.
- Addressed exception in maps when some values of a parameter are missing their domain element.

11.2.2
~~~~~~

- Addressed issue with incorrectly formatted template (https://github.com/clld/clld/pull/264)


11.2.1
~~~~~~

- Addressed one issue regarding rendering of IGT examples.


11.2.0
~~~~~~

- More flexible ``cliutil.bibtex2source``, accomodating non-LaTeX content in
  BibTeX files and punctuation in citekeys.


11.1.0
~~~~~~

- Dropped support for Python 3.7.
- Added support for Python 3.12.
- Updated leaflet providers.


11.0.1
~~~~~~

Bugfix: Make sure color picker can be detected by appropriate cursor and
help text.


11.0.0
~~~~~~

- Refactored support for map marker customisation

Backwards incompatibility:

- Dropped old support for icon-select panels.


10.0.0
~~~~~~

- Drop support for CSV exports
- Drop support for alembic versioning
- Drop support for CLDF download
- Better support for metadata of CLDF datasets


9.2.2
~~~~~

- Limit base layer providers to ones that don't require API tokens.
- Update default publisher in project template.


9.2.1
~~~~~

- Don't advertise sourceMappingURL in javascript if this URL doesn't exist.


9.2.0
~~~~~

- Don't load resources from CDN anymore.
- Re-instate per-DataTable configurable download links.
- Support for creating localized URLs.


9.1.0
~~~~~

- Dropped support for py3.6.
- Removed per-table download buttons.


9.0.2
~~~~~

- Fixed confusing table info.
- Added case-sensitive column search function.


9.0.1
~~~~~

Fixed bug where person pre/suffixes for unknown gloss abbreviations would be
dropped when rendering IGTs.


9.0.0
~~~~~

Fixed bug where resize cursor would not show for map resizer with Leaflet 1.7.

Backwards incompatible removals:

- remove mostly useless adapters
- removed functionality to initialize db objects from csv
- removed deprecated purl property
- drop support for pg_collkey
- removed unneeded deps and unused functionality for combining geojson from other clld apps



8.1.0
~~~~~

- deprecate `ClldRequest.purl` in preparation of removing `purl` as dependency 
- require `SQLAlchemy>=1.4`


8.0.1
~~~~~

- Resizeable maps as default
- Include python 3.10 as supported platform


8.0.0
~~~~~

- Dropped support for legacy bib formats Endnote, RIS, MODS via bibutils.
- Dropped support for schema migrations - these shouldn't rely on clld code
  anyway.
- Dropped support for (legacy) wordpress integration.


7.4.1
~~~~~

Fixed bug whereby L.Control.Resizer.css wouldn't work due to packing.


7.4.0
~~~~~

- Better support for internationalization
- Support for map resizing


7.1.1
~~~~~

Fixed problems with new project templating / data loading machinery.


7.1.0
~~~~~

Better project template for apps from CLDF StructureDatasets


7.0.0
~~~~~

Refactored clld cli


6.0.0
~~~~~

Dropped py2 support


5.2.0
~~~~~

Bugfixes and upgrade of javascript


5.1.0
~~~~~

More support for cli scripts


5.0.0
~~~~~

Require python >= 3.5


4.7.2
~~~~~

Bugfixes


4.7.1
~~~~~

- better accessibility of accordeon controls.


4.7.0
~~~~~

- Updated Leaflet to 1.5.1
- Moved modules `color` and `svg` to clldutils package


4.6.1
~~~~~

Bugfixes



4.5.0
~~~~~

- Updated Leaflet to 1.4.0
- Refactorings for SQLAlchemy 1.3.x compatibility

4.4.2
~~~~~

- Support passing keyword arguments from DataTable to Toolbar


4.4.1
~~~~~

- Load external resources only via HTTPS


4.4.0
~~~~~

- Support for links to Glottolog


4.3.0
~~~~~

- Support for links to Concepticon
- Fixed bug in `svg.pie`



4.2.1
~~~~~

Bugfix and support for link to privacy policy in footer.



4.2.0
~~~~~

Support for creating valid customizable CLDF 1.0 downloads.


4.1.2
~~~~~

Bugfixes.


4.1.1
~~~~~

Bugfixes.


4.1.0
~~~~~

Better support for color handling and SVG icons.


4.0.3
~~~~~

Bugfixes


4.0.2
~~~~~

- fixed scope of db fixture to work with latest pytest-clld
- removed whitespace before punctuation in footer of app template


4.0.1
~~~~~

- fixes https://github.com/clld/clld/issues/134
- fixes https://github.com/clld/clld/issues/142
- fixes https://github.com/clld/clld/issues/143


4.0.0
~~~~~

Backwards incompatible.

Make the database schema more strict (identify data issues early, improve performance):
- add NOT NULL to columns where this was not enforces previously
- add UNIQUE constraints over column combinations where this was not enforced previously

For instructions on upgrading a present database see clld/db/schema_migrations/update_unique_null.py

Switch to using pytest for testing of clld as well as clld apps. Support for simpler
testing of apps has been moved to a pytest plugin pytest-clld.

Some obsolete functionality has been dropped.


3.3.3
~~~~~

Try to clean up the mess of dependencies around html5lib.


3.3.2
~~~~~

- closes https://github.com/clld/clld/issues/133
- closes https://github.com/clld/clld/issues/119


3.3.1
~~~~~

- bugfixes


3.3.0
~~~~~

- CLDF has reached 1.0rc1, and we update the CLDF export accordingly.


3.2.7
~~~~~

- closes https://github.com/clld/clld/issues/127



3.2.6
~~~~~

- closes https://github.com/clld/clld/issues/125
- closes https://github.com/clld/clld/issues/126


3.2.5
~~~~~

- fixing another edge case in the csv metadata adapter


3.2.4
~~~~~

- more reliable name parsing


3.2.3
~~~~~

- fixes https://github.com/clld/clld/issues/122


3.2.2
~~~~~

- fixes https://github.com/clld/clld/issues/121


3.2.1
~~~~~

- some support for fulltext search using PostgreSQL TSVECTOR columns


3.2.0
~~~~~

- factored out DeclEnum and LGR_ABBRS to clldutils
- upgraded leaflet to version 1.0.3


3.1.1
~~~~~

Added shortcut config method to add simple template-based pages to clld apps.


3.1.0
~~~~~

Upgraded leaflet and leaflet-provider plugin.


3.0.2
~~~~~

Bugfixes:
- https://github.com/clld/clld/issues/108
- https://github.com/clld/clld/issues/109


3.0.1
~~~~~

fixing bugs in CLDF export.


3.0.0
~~~~~

Backwards incompatible changes:

- clld does no longer provide support for imeji metadata files.
- The test utilities have been refactored. For typical clld apps,
  which used `TestWithEnv` and `TestWithApp` with `__setup_db__==False`
  this should not change anything.


2.2.1-4
~~~~~~~

Fixing bugs in new CLDF export.


2.2.0
~~~~~

Updated support for creating CLDF downloads.


2.1.3
~~~~~

Updated requirements, fixed tox config.


2.1.2
~~~~~

More and better docs and a release procedure adapted to Ubuntu 14.04.


2.1.1
~~~~~

Bugfix release. Fixes #94 and #95.


2.1.0
~~~~~

Better configurability of the OLAC interface.


2.0.0
~~~~~

Backwards incompatible changes:

- clld now requires clldutils, thus all functionality now available in 
  clldutils has been removed from clld.
- clld does not depend on path.py anymore, but instead uses clldutils.path,
  which in turn uses pathlib2 for python 2.7 and the standard library's
  pathlib on python 3.4 for object oriented file system path handling.


1.8.0
~~~~~

Removed obsolete functionality.


1.7.1
~~~~~

Turns out we now rely on a rather recent feature of requests, so we better
make this transparent in the requirements.


1.7.0
~~~~~

Due to the shutdown of the Google Feeds API the CLLD.Feed javascript component
broke. This release provides functionality to help apps reimplement the lost
functionality.


1.6.1
~~~~~

Bugfix release, fixes https://github.com/clld/clld/issues/86

It seems sil.org will stick with www-01 as canonical subdomain for ISO 639-3
related resources.


1.6.0
~~~~~

New feature: see https://github.com/clld/clld/issues/86

Bugfix: see https://github.com/clld/clld/issues/85


1.5.1
~~~~~

Bugfix release, fixes https://github.com/clld/clld/issues/84


1.5.0
~~~~~

See https://github.com/clld/clld/milestones/clld%201.5


1.4.1
~~~~~

See https://github.com/clld/clld/milestones/clld%201.4.1


1.4.0
~~~~~

Improvements to make client development easier. In particular see
https://github.com/clld/clld/issues/75


1.3.0
~~~~~

See https://github.com/clld/clld/milestones/clld%201.3


1.2.1
~~~~~

See https://github.com/clld/clld/commit/f6c679dc33ff090c735a0fbf624d27f5e4987d13


1.2.0
~~~~~

Closes https://github.com/clld/clld/issues/69
and https://github.com/clld/clld/milestones/Release%201.2.0


1.1.0
~~~~~

Fixing a bug for pacific centered maps of a single language, where the center
coordinates were not corrected accordingly. This fix turned into a refactoring
of the GeoJSON generation, reverting back to not using __geo_interface__ since
this means sprinkling GeoJSN-creating code over multiple modules.


1.0.2
~~~~~

fixed bug where weird author lists could not be parsed.


1.0.1
~~~~~

fixed bug where the freeze function would fail on non-ascii dataset metadata.


1.0.0
~~~~~

Feature-complete release of the clld framework.

Backwards incompatible changes:

- `clld.web.app` can now be included like a regular pyramid package. The `get_configurator`
  function is gone.
- Pacific centered maps can now be configured using an `appconf.ini` setting. This setting
  is in effect across all GeoJSON objects of an app. The method `GeoJson.get_coordinates`
  which was used to plug pacific centered coordinates into `GeoJson` is gone.

New features:

- Upon installation `clld` does now install several command line scripts, to make functionality
  available which before had to be accessed using per-app scripts.

