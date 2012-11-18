==================
Installation guide
==================

.. highlight:: sh

This guide provides installation instructions for Plyvel.


Build and install Plyvel
========================

The recommended (and easiest) way to install Plyvel is to install it into a
virtual environment (*virtualenv*) using ``pip``, which will automatically grab
the latest release from the `Python Package Index <http://pypi.python.org/>`_
(PyPI)::

   $ virtualenv envname
   $ source envname/bin/activate
   (envname) $ pip install plyvel

For the more traditionally minded: downloading a source tarball, unpacking it
and installing it manually with ``python setup.py install`` should also work.

Note that Plyvel requires an installed shared library for LevelDB at build time,
so make sure you have a shared LevelDB library installed where the compiler and
linker can find them. For Debian or Ubuntu something like ``apt-get install
libleveldb1 libleveldb-dev`` should suffice, but any other installation method
should do as well.


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
