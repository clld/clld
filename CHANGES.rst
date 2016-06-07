
Changes
-------

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

