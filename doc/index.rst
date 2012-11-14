.. Plyvel documentation master file, created by
   sphinx-quickstart on Sun Nov 11 17:26:23 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

======
Plyvel
======

**Plyvel** is a fast and feature-rich Python interface to LevelDB_.

Plyvel's key features are:

* **Rich feature set**

  Plyvel wraps most of the LevelDB C++ API, so in addition to basic features
  like getting, putting and deleting data, Plyvel allows you to use write
  batches, database snapshots, very flexible iterators, bloom filters, custom
  cache sizes, and other goodness LevelDB has to offer.

* **High performance**

  Plyvel executes all performance-critical code at C speed (using Cython_),
  which means Plyvel is a good fit for high performance applications.

* **Friendly Pythonic API**

  Plyvel has a friendly and well-designed API that uses Python idioms like
  iterators and context managers (``with`` blocks), without sacrificing the
  power or performance of the underlying LevelDB C++ API.

* **Python 2 and Python 3 compatibility**

  Plyvel works with both Python 2 and Python 3, without any API differences.

.. _LevelDB: http://code.google.com/p/leveldb/
.. _Cython: http://cython.org/


Documentation overview
======================

.. toctree::
   :maxdepth: 1

   installation
   tutorial
   api
   license


External links
==============

* `Online documentation <https://plyvel.readthedocs.org/>`_ (Read the docs)
* `Project page <https://github.com/wbolster/plyvel>`_ with source code and
  issue tracker (Github)


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
