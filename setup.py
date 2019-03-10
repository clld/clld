from setuptools import setup, find_packages

install_requires = [
    'Babel',
    'csvw~=1.0',
    'clldutils~=2.4',
    'pycldf>=1.5.1',
    'setuptools>=25',
    'pyramid>=1.10',
    'pyramid_mako>=1.0',
    'pyramid_tm',
    'SQLAlchemy>=1.0.6',
    'purl>=0.5',
    'pytz',
    'zope.sqlalchemy',
    'six>=1.7.3',  # webassets needs add_metaclass!
    'alembic>=0.7.1',
    'webassets',
    'yuicompressor',
    'markupsafe',
    'requests>=2.4.3',  # we use the support for connect timeouts introduced in 2.4.0
    'rdflib>=4.1.1',  # rdflib 4.1.0 requires html5lib==0.95
    'colander',
    'python-dateutil',
    'paginate',
    'xlwt',
    'webhelpers2>=2.0',
    'nameparser',
    'feedparser',
    'waitress',
]


setup(
    name='clld',
    version='4.4.3.dev0',
    description=(
        'Python library supporting the development of cross-linguistic databases'),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
    ],
    keywords='web pyramid LRL Linguistics',
    author="Robert Forkel, MPI SHH",
    author_email="forkel@shh.mpg.de",
    url="http://clld.org",
    license="Apache Software License",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*',
    install_requires=install_requires,
    extras_require={
        'dev': [
            'waitress',
            'pyramid_debugtoolbar',
            'tox',
            'flake8',
            'wheel',
            'twine',
        ],
        'test': [
            'xlrd',
            'mock',
            'pytest>=3.6',
            'pytest-clld',
            'pytest-mock',
            'pytest-cov',
            'coverage>=4.2',
            'zope.component>=3.11.0',
        ],
        'docs': [
            'Sphinx',
            'docutils',
            'repoze.sphinx.autointerface',
        ],
    },
    message_extractors={'src/clld': [
        ('**.py', 'python', None),
        ('**.mako', 'mako', {'encoding': 'utf8'}),
        ('web/static/**', 'ignore', None)]},
    entry_points="""\
        [pyramid.scaffold]
        clld_app=clld.scaffolds:ClldAppTemplate
        [console_scripts]
        clld-google-books = clld.scripts.cli:google_books
        clld-internetarchive = clld.scripts.cli:internetarchive
        clld-create-downloads = clld.scripts.cli:create_downloads
    """
)
