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

Almost all Plyvel code is covered by the unit tests. Plyvel uses *Nose* for
running those tests. Type ``make test`` to run the unit tests.


Generating the documentation
============================

The documentation is written in ReStructuredText (reST) format and processed
using *Sphinx*. Type ``make doc`` to build the HTML documentation.
