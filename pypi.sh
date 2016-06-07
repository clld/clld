VENVS=~/venvs

cd $VENVS/pypi
. bin/activate
cd clld
git pull origin master
git checkout tags/v$1
python setup.py sdist register upload

