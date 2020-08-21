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

(In case you're feeling old-fashioned: downloading a source tarball, unpacking
it and installing it manually with ``python setup.py install`` should also
work.)

The Plyvel source package does not include a copy of LevelDB itself.
Plyvel requires LevelDB development headers and an installed shared
library for LevelDB during build time, and the same installed shared
library at runtime.

To build from source, make sure you have a shared LevelDB library and
the development headers installed where the compiler and linker can
find them. For Debian or Ubuntu something like ``apt-get install
libleveldb1v5 libleveldb-dev`` should suffice.

For Linux, Plyvel also ships as pre-built binary packages
(``manylinux1`` wheels) that have LevelDB embedded. Simply running
``pip install plyvel`` does the right thing with a modern ``pip`` on
a modern Linux platform, even without any LevelDB libraries on your
system.

.. note::

   Plyvel 1.x depends on LevelDB >= 1.20, which at the time of writing
   (early 2018) is more recent than the versions packaged by various
   Linux distributions. Using an older version will result in
   compile-time errors. The easiest solution is to use the pre-built
   binary packages. Alternatively, install LevelDB manually on your
   system. The Dockerfile in the Plyvel source repository, which is
   used for building the official binary packages, shows how to do
   this.

.. warning::

   The above installation method applies only to released packages available
   from PyPI. If you are building and installing from a source tree acquired
   through other means, e.g. checked out from source control, you will need to
   run Cython first. If you don't, you will see errors about missing source
   files. See the :doc:`developer documentation <developer>` for more
   information.


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
