from setuptools import setup, find_packages, find_namespace_packages

setup(
    name='{{cookiecutter.directory_name}}',
    version='0.0',
    description='{{cookiecutter.directory_name}}',
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='',
    author_email='',
    url='',
    keywords='web pyramid pylons',
    packages=find_namespace_packages(),
    include_package_data=True,
    #package_data={
    #    "{{cookiecutter.directory_name}}": [
    #        "static/**/*",
    #        "templates/**/*",
    #        "locale/**/*",
    #    ],
    #},
    zip_safe=False,
    install_requires=[
        'clld',
{% if cookiecutter.mpg == true %}
        'clldmpg',
{% endif %}
],
extras_require={
        'dev': ['flake8', 'waitress', 'Babel'],
        'test': [
            'pytest>=5.4',
            'pytest-clld>=1.3',
            'pytest-mock',
            'pytest-cov',
            'coverage>=4.2',
            'selenium',
            'zope.component>=3.11.0',
        ],
    },
    entry_points="""\
    [paste.app_factory]
    main = {{cookiecutter.directory_name}}:main
""")
