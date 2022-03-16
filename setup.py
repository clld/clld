from setuptools import setup, find_packages


setup(
    name='clld',
    version='9.0.2',
    description=(
        'Python library supporting the development of cross-linguistic databases'),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
    ],
    keywords='web pyramid LRL Linguistics',
    author="Robert Forkel",
    author_email="robert_forkel@eva.mpg.de",
    url="https://clld.org",
    license="Apache Software License",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.6',
    install_requires=[
        'Babel',
        'csvw>=1.0',
        'clldutils>=3.5',
        'pycldf>=1.5.1',
        'setuptools>=25',
        'pyramid>=1.10',
        'pyramid_mako>=1.0',
        'pyramid_tm',
        'SQLAlchemy>=1.4',
        'zope.sqlalchemy',
        'webassets>=0.12.1',  # no longer supports py2, no longer requires six!
        'markupsafe',
        'rdflib>=4.1.1',  # rdflib 4.1.0 requires html5lib==0.95
        'paginate',
        'webhelpers2>=2.0',
        'nameparser',
    ],
    extras_require={
        'dev': [
            'cookiecutter',
            'cldfcatalog',
            'waitress',
            'pyramid_debugtoolbar',
            'tox',
            'flake8',
            'wheel',
            'twine',
        ],
        'test': [
            'cookiecutter',
            'pytest>=6',
            'pytest-clld>=1.0.3',
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
        [console_scripts]
        clld = clld.__main__:main
    """
)
