#!/usr/bin/env bash
VENVS=$1 # first argument, path to virtual environment folder
GLOTTOLOG=$3 # 3rd argument, path to glottolog/glottolog

cd $VENVS

virtualenv testapp
cd testapp
./bin/pip install -U setuptools
./bin/pip install -U pip
./bin/pip install -e $2 # second argument, path to local clld repository
./bin/pip install cookiecutter
./bin/clld create --quiet --force testapp_clld
cd testapp_clld
../bin/pip install -e .[test]
../bin/clld initdb development.ini
../bin/pytest || exit 1
cd $VENVS
rm -rf testapp
echo "testing bare template done"

virtualenv testapp
cd testapp
./bin/pip install -U setuptools
./bin/pip install -U pip
./bin/pip install -e $2 # second argument, path to local clld repository
./bin/pip install cookiecutter
./bin/clld create --quiet testapp_clld mpg=y
cd testapp_clld
../bin/pip install -e .[test]
../bin/clld initdb development.ini
../bin/pytest || exit 1
cd $VENVS
rm -rf testapp
echo "testing mpg template done"

virtualenv testapp
cd testapp
./bin/pip install -U setuptools
./bin/pip install -U pip
./bin/pip install $2 # second argument, path to local clld repository
./bin/pip install cookiecutter
./bin/clld create --quiet testapp_clld cldf_module=structuredataset
cd testapp_clld
../bin/pip install -e .[test]
../bin/clld initdb development.ini --cldf $2/tests/cldf_datasets/structuredataset/StructureDataset-metadata.json --glottolog $GLOTTOLOG
../bin/pytest || exit 1
cd $VENVS
rm -rf testapp
echo "testing cldf template done"
