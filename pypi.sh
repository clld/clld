VENVS=~/venvs

cd $VENVS/pypi
. bin/activate
cd clld
git pull origin
git checkout tags/$1
python setup.py sdist register upload

