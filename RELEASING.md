Releasing clld
==============

- Update translations
  ```shell
  python setup.py extract_messages
  python setup.py update_catalog
  python setup.py compile_catalog
  ```

- Make sure all changes are committed and pushed with a `*.devN` version number.

- Do platform test via tox (making sure statement coverage is >= 99%):
  ```shell
  tox -r
  ```

- Make sure all scaffold tests pass (on at least one supported Python version):
  ```shell
  sh build.sh
  ```
  Note that this assumes virtualenvironments to be created in `~/venvs/`.

- Make sure javascript and css can be minified:
  ```shell
  webassets -m clld.web.assets build
  rm -i src/clld/web/static/*/packed.*
  ```

- Make sure javascript tests pass (take care of specifying the name of the Chromium binary - e.g. 
  chromium-browser or chromium):
  ```shell
  /usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java -jar tools/jsTestDriver/JsTestDriver-1.3.5.jar --tests all --browser chromium-browser --port 9877
  ```
  Note that this requires Java 8 to be installed.

- Make sure flake8 passes
  ```shell
  flake8 src/
  ```

- Make sure docs render OK
  ```shell
  cd docs
  make clean html
  cd ..
  ```

- Update the version number, by removing the trailing `.dev0` in:
  - `setup.py`
  - `src/clld/__init__.py`
  - `docs/conf.py`

- Change CHANGES.rst heading to reflect the new version number.

- Create the release commit:
  ```shell
  git commit -a -m "release <VERSION>"
  ```

- Create a release tag:
  ```shell
  git tag -a v<VERSION> -m "<VERSION> release"
  ```

- Release to PyPI:
  ```shell
  rm -rf build
  rm dist/*
  python -m build -n
  twine upload dist/*
  ```

- Push to github:
  ```shell
  git push origin
  git push --tags origin
  ```

- Re-release using the same tag on GitHub, to trigger the ZENODO hook.
  update the DOI badge.

- Increment version number and append `.dev0` to the version number for the new development cycle:
  - `src/clld/__init__.py`
  - `setup.py`
  - `docs/conf.py`

- Commit/push the version change:
  ```shell
  git commit -a -m "bump version for development"
  git push origin
  ```

