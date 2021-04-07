# clld

The `clld` toolkit - a web framework for the publication of
[Cross-Linguistic Linked Data](https://clld.org).

Documentation for the code base and its use is available at http://clld.readthedocs.org/en/latest/. The source for this documentation is in the `docs` directory.

[![Build Status](https://github.com/clld/clld/workflows/tests/badge.svg)](https://github.com/clld/clld/actions?query=workflow%3Atests)
[![codecov](https://codecov.io/gh/clld/clld/branch/master/graph/badge.svg)](https://codecov.io/gh/clld/clld)
[![Requirements Status](https://requires.io/github/clld/clld/requirements.svg?branch=master)](https://requires.io/github/clld/clld/requirements/?branch=master)
[![PyPI](https://img.shields.io/pypi/v/clld.svg)](https://pypi.python.org/pypi/clld)
[![Documentation Status](http://readthedocs.org/projects/clld/badge/?version=latest)](http://clld.readthedocs.io/en/latest/?badge=latest)


## Cite

Most recent version:
https://doi.org/10.5281/zenodo.592412


## Usage

Once the initial steps (installation, bootstrapping a new project)
have been done helped by [the online documentation](http://clld.readthedocs.org/en/latest/),
the biggest resource to guide further development of a `clld` app
is the [wealth of existing apps](https://github.com/clld/clld/network/dependents).
(Note: GitHub's "Used by" links - created from the dependency graph data - are really
helpful here!)
The following pointers are meant as a
starting point to solve specific problems by perusing the code of other
apps.

- **Integrating language metadata from Glottolog**: There's 
  [a plugin](https://github.com/clld/clld-glottologfamily-plugin) for that
  and here's the list of apps on GitHub using it: https://github.com/clld/clld-glottologfamily-plugin/network/dependents
- **Displaying (data on) phylogenetic laguage trees**: There's
  [a plugin](https://github.com/clld/clld-phylogeny-plugin) for that
  and here's the list of apps on GitHub using it: https://github.com/clld/clld-phylogeny-plugin/network/dependents
- **Displaying cognacy relations between words**: There's
  [a plugin](https://github.com/clld/clld-cognacy-plugin) for that
  and here's the list of apps on GitHub using it: https://github.com/clld/clld-cognacy-plugin/network/dependents
- **Displaying phoneme inventories as IPA charts**: There's
  [a plugin](https://github.com/clld/clld-ipachart-plugin) for that
  and here's the list of apps on GitHub using it: https://github.com/clld/clld-ipachart-plugin/network/dependents
- **Integrating audio recordings of lexical data**: There's
  [a plugin](https://github.com/clld/clld-audio-plugin) for that
  and here's the list of apps on GitHub using it: https://github.com/clld/clld-audio-plugin/network/dependents
- **Aggregating data from multiple CLDF datasets**: The app serving the
  [Intercontinental Dictionary Series](https://ids.clld.org) does this.
  Very simple per-dataset metadata of the form
  ```json
  {
    "id": "ids-cosgrovevoro",
    "repo": "https://github.com/intercontinental-dictionary-series/cosgrovevoro",
    "doi": "10.5281/zenodo.4280576",
    "order": 2
  }
  ```
  is read and used to populate the database, see
  https://github.com/clld/ids/blob/master/ids/scripts/initializedb.py#L38-L67
- **Aggregating data from different CLDF modules**: While most `clld` apps are
  concerned with just one type of data (e.g. typological questionnaires as in WALS,
  or wordlists as in IDS), some have a different focus (e.g.
  [TuLaR (Tupían Language Resources)](https://tular.clld.org)). The TuLaR
  app aggregates data which is curated in several datasets, bundled under
  a [Zenodo community](https://zenodo.org/communities/tular), see https://github.com/tupian-language-resources/tular/blob/main/tular/scripts/initializedb.py
- **Using Charis SIL fonts**: using [SIL's Charis fonts](https://software.sil.org/charis/) on a `clld` page is simple. Here's an example
  https://ids.clld.org/valuesets/1-100-316
  - Include the relevant style sheet (which will pull in the font resources):
    https://github.com/clld/ids/blob/b2884e06a53a0a3c7a0dc27955c314869d0a31aa/ids/templates/ids.mako#L10-L12
  - Then assign the appropriate css class:
    https://github.com/clld/ids/blob/b2884e06a53a0a3c7a0dc27955c314869d0a31aa/ids/templates/unit/detail_html.mako#L6


## See

- The [CLLD project](https://clld.org)
- [Online documentation](http://clld.readthedocs.org/en/latest/)
- [Presentation on clld from 2014](https://clld.org/docs/reflex/clld.pdf)
