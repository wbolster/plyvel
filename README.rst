Plyvel: Python bindings for LevelDB using Cython
================================================

**Note:** this project is a work in progress and not yet fully functional!

This package provides LevelDB_ bindings for both Python 2 and Python 3, built
using Cython_. Most parts of the LevelDB API can used in a Pythonic way, e.g.
with clean iterators for the RangeIter() API and things like context managers
(``with`` blocks) for the WriteBatch API.

.. _LevelDB: http://code.google.com/p/leveldb/
.. _Cython: http://cython.org/
