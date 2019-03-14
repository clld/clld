#!/usr/bin/env bash
VENVS=$1 # first argument, path to virtual environment folder

cd $VENVS

virtualenv testapp
cd testapp
. bin/activate
pip install -U setuptools
pip install -U pip
pip install $2 # second argument, path to local clld repository
pcreate -t clld_app testapp
cd testapp
pip install -e .[test]
python testapp/scripts/initializedb.py development.ini
pytest
cd $VENVS
rm -rfI testapp

