.. _install_mac:

An installation for Mac OSX Maverick users using MacPorts
---------------------------------------------------------

1. Set up Git for Mac.

https://help.github.com/articles/set-up-git


2. Install fresh MacPorts or upgrade if necessary:

http://www.macports.org/install.php
http://guide.macports.org/
https://trac.macports.org/wiki/Migration

Macports requires X11 and Xcode (see instructions in step 1; install via the App store).

.. note::

    One can set the Mac terminal Python command with:

        sudo port select --set python pythonNN

    where NN == 34 or 27 (3.4 or 2.7 or whatever version the user wants as default)

Make sure to install virtualenv-2.7, but note it isn't by default on the path -- when firing
CLLD install instructions, add to path or use:

    /opt/local/bin/virtualenv-2.7 <venv>

where <venv>, as below, is the name of your virtual environment.


3. Install Python 2.7 and other libraries that are required for CLLD

<insert like to required libraries>


4. Install Postgres (or other relevant database program) for CLLD:

http://www.postgresql.org/download/macosx/


Then follow the CLLD install instructions (:ref:`install`).

