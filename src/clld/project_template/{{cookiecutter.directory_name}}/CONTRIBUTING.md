Contributing
------------

Install the development environment:

```sh
$ pip install virtualenv  # might require sudo/admin privileges
$ git clone https://github.com/clld/clld.git  # you may also clone a suitable fork
$ cd {{cookiecutter.directory_name}}
$ python -m virtualenv .venv
$ source .venv/bin/activate  # Windows: .venv\Scripts\activate.bat
$ pip install -r requirements.txt  # installs the cloned version with dev-tools in development mode
```

Then create a database:

```sh
$ su - postgres
$ createdb {{cookiecutter.directory_name}}
```

and initialize it, either
- loading a dump of the production DB, using the app's `load_db` task from the
`appconfig` package
- or by running `clld initdb development.ini` (may require access to the appropriate data repository).

Now you should be able to run the tests:

```sh
$ pytest
```
