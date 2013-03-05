import os
import sys

from setuptools import setup, find_packages

py_version = sys.version_info[:2]

PY3 = py_version[0] == 3

if PY3:
    if py_version < (3, 2):
        raise RuntimeError('clld requires Python 3.2 or better')
else:
    if py_version < (2, 6):
        raise RuntimeError('clld requires Python 2.6 or better')

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''

install_requires = [
    'setuptools',
    'Pyramid >= 1.4',
    'sqlalchemy>=0.7.9',
    'Mako >= 0.3.6', # strict_undefined
    'PasteDeploy >= 1.5.0', # py3 compat
    #'purl',
    'path.py',
    'pyramid-exclog',
    'zope.sqlalchemy',
    'purl',
    'fabric',
    'fabtools',
    'WebTest',
]

if not PY3:
    install_requires.append('Babel')

tests_require = [
    'WebTest >= 1.3.1', # py3 compat
    'pep8',
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
      version='0.1',
      description=('Python library for the Words of the World project'),
      long_description='',
      classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        ],
      keywords='web pyramid',
      author="Robert Forkel, MPI EVA",
      author_email="xrotwang+clld@googlemail.com",
      url="http://",
      license="BSD",
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
