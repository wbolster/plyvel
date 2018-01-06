===========================
Contributing and developing
===========================

.. _Plyvel project page: https://github.com/wbolster/plyvel


Reporting issues
================

Plyvel uses Github's issue tracker. See the `Plyvel project page`_ on Github.


Obtaining the source code
=========================

The Plyvel source code can be found on Github. See the `Plyvel project page`_ on
Github.


Compiling from source
=====================

A simple ``make`` suffices to build the Plyvel extension. Note that the
``setup.py`` script does *not* invoke Cython, so that installations using ``pip
install`` do not need to depend on Cython.

A few remarks about the code:

* Plyvel is mostly written in Cython. The LevelDB API is described in
  `leveldb.pxd`, and subsequently used from Cython.

* The custom comparator support is written in C++ since it contains a C++ class
  that extends a LevelDB C++ class. The Python C API is used for the callbacks
  into Python. This custom class is made available in Cython using
  `comparator.pxd`.


Running the tests
=================

Almost all Plyvel code is covered by the unit tests. Plyvel uses *pytest* and
*tox* for running those tests. Type ``make test`` to run the unit tests, or run
``tox`` to run the tests against multiple Python versions.


Producing binary packages
=========================

To build a non-portable binary package for a single platform::

  python setup.py bdist_wheel

See the comments at the top of the ``Dockerfile`` for instructions on
how to build portable ``manylinux1`` wheels for multiple Python
versions that should work on many Linux platforms.


Generating the documentation
============================

The documentation is written in ReStructuredText (reST) format and processed
using *Sphinx*. Type ``make doc`` to build the HTML documentation.
