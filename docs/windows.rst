.. _install_win:

An installation for Windows 7
-----------------------------

1. Install `python 2.7 <http://python.org>`_ following the instructions
   `here <http://docs.python-guide.org/en/latest/starting/install/win/>`_.

2. Install `git <http://git-scm.com>`_ following the instructions
   `here <http://guides.beanstalkapp.com/version-control/git-on-windows.html>`_.

3. Install `PostgreSQL <http://www.postgresql.org/>`_ (> 9.0) following the instructions
   `here <https://wiki.postgresql.org/wiki/Running_%26_Installing_PostgreSQL_On_Native_Windows>`_.

.. note::

    Some python packages used by the ``clld`` software have extensions coded in C. If
    these packages are installed from source, the system must have a C-compiler. Without
    one, trying to install such a package results in the system complaining about
    ``vcvarsall.bat`` missing. You can fix this problem using any of the solutions explained
    in `this stackoverflow thread <http://stackoverflow.com/questions/2817869/error-unable-to-find-vcvarsall-bat>`_.


Then follow the CLLD install instructions (:ref:`install`).

