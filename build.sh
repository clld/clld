#!/usr/bin/env bash
VENVS=~/venvs

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

