=============
Plyvel-wheels
=============

.. image:: https://travis-ci.org/wbolster/plyvel.svg?branch=master
    :target: https://travis-ci.org/wbolster/plyvel

Why does this fork exist?
--------------------------

The sole reason for this fork existing is to provide cross platform wheels for
ease of installation - Namely on Mac and Windows which do not currently have bundled leveldb
libraries. (This repo was previously named plyvel-win32 as it was only for windows)

In other words, I am compiling the C++ leveldb -> x86-64 binaries + doing
the cython build and wheel creation so that you don't have to. I have no intention
of doing any development work on plyvel beyond this - please continue to use
the main repository for all other purposes.

To install:

.. code-block:: python

    > py -3.9 -m pip install plyvel-wheels

Then use like you normally use plyvel:

.. code-block:: python

    import plyvel
    db = plyvel.DB('/tmp/testdb/', create_if_missing=True)

Note:
-----
There is a single failing test for windows:

- `test_open_read_only_dir`

Where there is a discrepancy in the type of error message that is thrown when trying to access a
db in a read-only directory. I am unsure if this is of any significance in practice.


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
