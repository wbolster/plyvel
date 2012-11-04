Python bindings for LevelDB using Cython
========================================

**Note:** this project is a work in progress and not yet fully functional!

This package provides LevelDB_ bindings for Python, built using Cython_. The
goal is to wrap most parts of the LevelDB API in a Pythonic way, e.g. with clean
iterators for the RangeIter() API and things like context managers (``with``
blocks) for the WriteBatch API.

.. _LevelDB: http://code.google.com/p/leveldb/
.. _Cython: http://cython.org/
