#!/usr/bin/env bash
VENVS=~/venvs

cd $VENVS/cheesecake
. bin/activate
pip install -U setuptools
cd clld
git checkout master
git pull origin master
python setup.py sdist
cheesecake_index --path="dist/clld-$1.tar.gz" --with-pep8

cd $VENVS
virtualenv testapp
cd testapp
. bin/activate
pip install -U setuptools
pip install -U pip
pip install "$VENVS/cheesecake/clld/dist/clld-$1.tar.gz"
pcreate -t clld_app testapp
cd testapp
pip install -e .[test]
python testapp/scripts/initializedb.py development.ini
pytest
cd $VENVS
rm -rf testapp

cd $VENVS
virtualenv --python=python3.4 testapp
cd testapp
. bin/activate
pip install -U setuptools
pip install -U pip
pip install "$VENVS/cheesecake/clld/dist/clld-$1.tar.gz"
pcreate -t clld_app testapp
cd testapp
pip install -e .[test]
python testapp/scripts/initializedb.py development.ini
pytest
cd $VENVS
rm -rf testapp
