from __future__ import unicode_literals
import os
import sys

from setuptools import setup, find_packages


py_version = sys.version_info[:2]

PY3 = py_version[0] == 3

if PY3:
    if py_version < (3, 4):
        raise RuntimeError('clld requires Python 3.4 or better')
else:
    if py_version < (2, 7):
        raise RuntimeError('clld requires Python 2.7 or better')

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()
except IOError:
    README = CHANGES = ''

install_requires = [
    'setuptools>=0.8',
    'pyramid>=1.5.1',
    'pyramid_mako>=1.0',
    'pyramid_tm',
    'SQLAlchemy>=0.9.8',
    'PasteDeploy>=1.5.0',  # py3 compat
    'waitress',
    'purl>=0.5',
    'path.py',
    'pyramid_exclog',
    'pytz',
    'zope.sqlalchemy',
    'WebTest',
    'six>=1.7.3',  # webassets needs add_metaclass!
    'alembic>=0.7.1',
    'webassets',
    'yuicompressor',
    'markupsafe',
    'requests',
    'rdflib>=4.1.1',  # rdflib 4.1.0 requires html5lib==0.95
    'colander',
    'python-dateutil',
    'paginate',
    'html5lib==0.999',  # our tests rely on the childNodes attribute
    'xlrd',
    'xlwt-future',
    'webhelpers2>=2.0rc1',
    'nameparser',
]

if not PY3:
    install_requires.append('Babel')

tests_require = [
    'WebTest >= 1.3.1', # py3 compat
    'pep8',
    'mock',
    'selenium',
]

if not PY3:
    tests_require.append('zope.component>=3.11.0')

docs_extras = [
    'Sphinx',
    'docutils',
    'repoze.sphinx.autointerface',
]

testing_extras = tests_require + [
    'nose',
    #'nosexcover',
    'coverage',
    'virtualenv', # for scaffolding tests
]

setup(name='clld',
      version='0.31.5',
      description=(
          'Python library supporting the development of cross-linguistic databases'),
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        ],
      keywords='web pyramid',
      author="Robert Forkel, MPI EVA",
      author_email="xrotwang+clld@googlemail.com",
      url="http://clld.org",
      license="Apache Software License",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires = install_requires,
      extras_require = {'testing': testing_extras, 'docs': docs_extras},
      tests_require = tests_require,
      test_suite="clld.tests",
      message_extractors = {'clld': [
            ('**.py', 'python', None),
            ('**.mako', 'mako', None),
            ('web/static/**', 'ignore', None)]},
      entry_points = """\
        [pyramid.scaffold]
        clld_app=clld.scaffolds:ClldAppTemplate
      """
)
