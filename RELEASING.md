Releasing clld
==============

- Update translations
```
python setup.py extract_messages
python setup.py update_catalog
python setup.py compile_catalog
```

- Make sure all changes are committed and pushed with a *.devN version number.

- Do platform test via tox (making sure statement coverage is >= 99%):
```
tox -r
```

- Make sure all scaffold tests pass (Py 2.7, 3.4): After pushing the develop branch run
```
./venvs/clld/clld/build.sh "<rel-no>.dev0"
```

- Make sure javascript and css can be minified:
```
webassets -m clld.web.assets build
rm -i src/clld/web/static/*/packed.*
```

- Make sure javascript tests pass with coverage of clld.js at > 82%:
```
java -jar tools/jsTestDriver/JsTestDriver-1.3.5.jar --tests all --browser chromium-browser --port 9877
```

- Make sure flake8 passes
```
flake8 src/
```

- Make sure docs render OK
```
cd docs
make clean html
cd ..
```

- Update the version number, by removing the trailing `.dev0`:
  - `src/clld/__init__.py`
  - `setup.py`
  - `docs/conf.py`

- Change CHANGES.rst heading to reflect the new version number.

- Bump version number:
```
git commit -a -m"bumped version number"
```

- Create a release tag:
```
git tag -a v<version> -m"..."
```

- Push to github:
```
git push origin
git push --tags
```

- Release to PyPI:
```
git checkout tags/v$1
rm dist/*
python setup.py sdist bdist_wheel
twine upload dist/*
```

- Re-release using the same tag on GitHub, to trigger the ZENODO hook.
  update the DOI badge.

- Update the version number to the new development cycle:
  - `src/clld/__init__.py`
  - `setup.py`
  - `docs/conf.py`
