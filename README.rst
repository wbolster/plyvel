============
Plyvel-win32
============

.. image:: https://travis-ci.org/wbolster/plyvel.svg?branch=master
    :target: https://travis-ci.org/wbolster/plyvel

Why does this fork exist?
--------------------------

The sole reason for this fork existing is to provide win32 python wheels for
ease of installation.

In other words, I am compiling the C++ leveldb -> x86 and x86-64 binaries + doing
the cython build and wheel creation so that you don't have to. I have no intention
whatsoever of doing any development work on plyvel beyond this - please continue to use
the main repository for all other purposes.

Plyvel
------
**Plyvel** is a fast and feature-rich Python interface to LevelDB_.

Plyvel has a rich feature set, high performance, and a friendly Pythonic API.
See the documentation and project page for more information:

* Documentation_
* `Project page`_
* `PyPI page`_

.. _Project page: https://github.com/wbolster/plyvel
.. _Documentation: https://plyvel.readthedocs.io/
.. _PyPI page: http://pypi.python.org/pypi/plyvel/
.. _LevelDB: http://code.google.com/p/leveldb/

Note that using a released version is recommended over a checkout from version
control. See the installation docs for more information.
