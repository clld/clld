
Deployment of CLLD apps
-----------------------

The 'clldfabric' package provides functionality to ease the deployment of CLLD apps. The
functionality is implemented as fabric tasks.


Overview
~~~~~~~~

- The target platform assumed by these tasks is Ubuntu 12.04 LTS.
- Source code is transferred to the machines by cloning the respective github repositories.
- Apps are run by gunicorn, monitored by supervisor, behind nginx as transparent proxy.
- PostgreSQL is used as database.


Automation
~~~~~~~~~~

We use fabric to automate deployment and other tasks which have to be executed on remote
hosts.

