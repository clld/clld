Contributing
------------

Development envionment:

```shell
$ pip install virtualenv  # might require sudo/admin privileges
$ git clone https://github.com/clld/clld.git
$ cd clld
$ python -m virtualenv .venv
$ source .venv/bin/activate  # Windows: .venv\Scripts\activate.bat
$ pip install -r requirements.txt  # installs the cloned version with dev-tools in development mode
```

In order to be able to run the javascript tests, `mocha` etc. must be installed in a node (>=18)
environment. `npm` will pickup the relevant requirements from `package.json`:
```shell
$ npm install
```
