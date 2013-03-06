======
Plyvel
======

**Plyvel** is a fast and feature-rich Python interface to LevelDB_.

Plyvel's key features are:

* **Rich feature set**

  Plyvel wraps most of the LevelDB C++ API and adds some features of its own. In
  addition to basic features like getting, putting and deleting data, Plyvel
  allows you to use write batches, database snapshots, very flexible iterators,
  prefixed databases, bloom filters, custom cache sizes, custom comparators, and
  other goodness LevelDB has to offer.

* **Friendly Pythonic API**

  Plyvel has a friendly and well-designed API that uses Python idioms like
  iterators and context managers (``with`` blocks), without sacrificing the
  power or performance of the underlying LevelDB C++ API.

* **High performance**

  Plyvel executes all performance-critical code at C speed (using Cython_),
  which means Plyvel is a good fit for high performance applications.

* **Extensive documentation**

  Plyvel comes with extensive documentation, including a user guide and API
  reference material.

* **Python 2 and Python 3 compatibility**

  Plyvel works with both Python 2 and Python 3, without any API differences.

.. _LevelDB: http://code.google.com/p/leveldb/
.. _Cython: http://cython.org/


Documentation overview
=========================

The documentation consists of three main parts:

* **Installation guide**

  The :doc:`installation guide <installation>` describes how to install Plyvel.

* **User guide**

  The :doc:`user guide <user>` shows how to use Plyvel and describes most
  features.

* **API reference**

  The :doc:`API reference <api>` contains all details about the Plyvel API.

* **Version history**

  See the :doc:`version history <news>` to see in which version features were
  added, bugs were fixed, and other changes were made.

See the full table of contents below for additional documentation.

External links
==============

* `Online documentation <https://plyvel.readthedocs.org/>`_ (Read the docs)
* `Project page <https://github.com/wbolster/plyvel>`_ with source code and
  issue tracker (Github)
* `Python Package Index (PyPI) page <http://pypi.python.org/pypi/plyvel/>`_ with
  released tarballs


Table of contents
=================

.. toctree::

   installation
   user
   api
   developer
   news
   license

* :ref:`genindex`
* :ref:`search`
