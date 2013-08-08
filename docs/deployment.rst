Deployment of CLLD apps
-----------------------

Target platform
~~~~~~~~~~~~~~~

we deploy to the following platform:

ubuntu 12.04 lts with
- git-core
- supervisor
- nginx
- postgresql
- libpq
- python-virtualenv
- python-devel


Automation
~~~~~~~~~~

We use fabric to automate deployment and other tasks which have to be executed on remote
hosts.

.. automodule:: clld.deploy.tasks
    :members:
