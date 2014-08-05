#!/bin/bash
cd ~/venvs
virtualenv --no-site-packages $1
cd $1
. bin/activate
if [ $# -eq 2 ]
  then
    curl -o zenodo.zip $2    
    unzip zenodo.zip
    var=($(ls -d clld-*))
    python ${var[0]}/fromdump.py
    cd $1
    pip install -r requirements.txt
  else
    git clone git@github.com:clld/$1.git
    cd $1
fi
python setup.py develop
if [ $# -eq 1 ]
  then
    pip freeze > requirements.txt
fi
python ewave/scripts/unfreeze.py sqlite.ini
pip install nose
pip install nosexcover
pip install mock
cp sqlite.ini development.ini
nosetests

