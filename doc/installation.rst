==================
Installation guide
==================

.. highlight:: sh

This guide provides installation instructions for Plyvel.


Build and install Plyvel
========================

The recommended (and easiest) way to install Plyvel is to install it into a
virtual environment (*virtualenv*)::

   $ virtualenv envname
   $ source envname/bin/activate

Now you can automatically install the latest Plyvel release from the `Python
Package Index <http://pypi.python.org/>`_ (PyPI) using ``pip``::

   (envname) $ pip install plyvel

(In case you're feeling old-fashioned:: downloading a source tarball, unpacking
it and installing it manually with ``python setup.py install`` should also
work.)

Note that Plyvel does not include a copy of LevelDB itself. Plyvel requires an
installed shared library for LevelDB at build time, so make sure you have a
shared LevelDB library and the development headers installed where the compiler
and linker can find them. For Debian or Ubuntu something like ``apt-get install
libleveldb1 libleveldb-dev`` should suffice, but any other installation method
should do as well.

.. warning::

   The above installation method applies only to released tarballs available
   from PyPI. If you are building and installing from a source tree acquired
   through other means, e.g. checked out from source control, you will need to
   run Cython first. If you don't, you will see errors about missing source
   files. See the :doc:`developer documentation <developer>` for more
   information.

.. note::

   The LevelDB version packaged in Ubuntu Precise (12.04) is too old for Plyvel,
   and the package does not include a shared library either. Manually installing
   the
   `libleveldb1 <http://packages.ubuntu.com/search?keywords=libleveldb1>`_,
   `libleveldb-dev <http://packages.ubuntu.com/search?keywords=libleveldb-dev>`_,
   `libsnappy1 <http://packages.ubuntu.com/search?keywords=libsnappy1>`_, and
   `libsnappy-dev <http://packages.ubuntu.com/search?keywords=libsnappy-dev>`_
   packages from Ubuntu Raring is known to work without problems.


Verify that it works
====================

After installation, this command should not give any output::

   (envname) $ python -c 'import plyvel'

If you see an ``ImportError`` complaining about undefined symbols, e.g.

.. code-block:: text

   ImportError: ./plyvel.so: undefined symbol: _ZN7leveldb10WriteBatch5ClearEv

…then the installer (actually, the linker) was unable to find the LevelDB
library on your system when building Plyvel. Install LevelDB or set the proper
environment variables for the compiler and linker and try ``pip install
--reinstall plyvel``.


.. rubric:: Next steps

Continue with the :doc:`user guide <user>` to see how to use Plyvel.

.. vim: set spell spelllang=en:
