VENVS=~/venvs

cd $VENVS/cheesecake
. bin/activate
cd clld
git checkout develop
git pull origin develop
python setup.py sdist
cheesecake_index --path="dist/clld-$1.tar.gz" --with-pep8

cd $VENVS
virtualenv testapp
cd testapp
. bin/activate
pip install "$VENVS/cheesecake/clld/dist/clld-$1.tar.gz"
#pip install "clld==$1"
pcreate -t clld_app testapp
cd testapp
python setup.py develop
python testapp/scripts/initializedb.py development.ini
pip install nose
pip install mock
nosetests
cd $VENVS
rm -rf testapp

