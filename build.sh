#!/usr/bin/env bash
VENVS=$(realpath ~/venvs/)
path=$(realpath "${BASH_SOURCE:-$0}")
CLLD_DIR_PATH=$(dirname $path)

cd $VENVS

virtualenv testapp
cd testapp
./bin/pip install -U setuptools
./bin/pip install -U pip
./bin/pip install -e $CLLD_DIR_PATH
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
./bin/pip install -e $CLLD_DIR_PATH
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
./bin/pip install $CLLD_DIR_PATH[bootstrap]
./bin/clld create --quiet testapp_clld cldf_module=structuredataset
cd testapp_clld
../bin/pip install -e .[test]
../bin/clld initdb development.ini --cldf $CLLD_DIR_PATH/tests/cldf_datasets/structuredataset/StructureDataset-metadata.json
../bin/pytest || exit 1
cd $VENVS
rm -rf testapp
echo "testing cldf template done"
