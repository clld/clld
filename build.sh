#!/usr/bin/env bash
VENVS=$1 # first argument, path to virtual environment folder

cd $VENVS

virtualenv testapp
./testapp/bin/pip install -U setuptools
./testapp/bin/pip install -U pip
./testapp/bin/pip install -e $2 # second argument, path to local clld repository
./testapp/bin/pip install cookiecutter
./testapp/bin/clld create --quiet --force testapp
cd testapp
./bin/pip install -e .[test]
./bin/clld initdb development.ini
./bin/pytest
cd $VENVS
rm -rfI testapp

virtualenv testapp
./testapp/bin/pip install -U setuptools
./testapp/bin/pip install -U pip
./testapp/bin/pip install -e $2 # second argument, path to local clld repository
./testapp/bin/pip install cookiecutter
./testapp/bin/clld create --quiet testapp mpg=y
cd testapp
./bin/pip install -e .[test]
./bin/clld initdb development.ini
./bin/pytest
cd $VENVS
rm -rfI testapp

#virtualenv testapp
#testapp/bin/pip install -U setuptools
#testapp/bin/pip install -U pip
#testapp/bin/pip install $2 # second argument, path to local clld repository
#testapp/bin/pip install cookiecutter
#testapp/bin/clld create --quiet testapp cldf_module=structuredataset
#testapp/bin/pip install -e testapp/.[test]
#testapp/bin/clld initdb development.ini --cldf --glottolog ...
#cd testapp/testapp
#pytest
#cd $VENVS
#rm -rfI testapp
