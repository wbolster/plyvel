========
Tutorial
========

.. py:currentmodule:: plyvel

This tutorial gives an overview of Plyvel. Basic familiarity with LevelDB is
assumed; visit the `LevelDB homepage`_ for more information.

.. _`LevelDB homepage`: http://code.google.com/p/leveldb/

Getting started
===============

After :doc:`installing Plyvel <installation>`, we can start by importing the
``plyvel`` module::

    >>> import plyvel

Let's open a new database by creating a new :py:class:`plyvel.DB` instance::

    >>> db = plyvel.DB('/tmp/testdb/', create_if_missing=True)

That's all there is to it. At this point ``/tmp/testdb/`` contains a fresh
LevelDB database (assuming the directory did not contain a LevelDB database
already).

For real world applications, you probably want to tweak things like the size of
the memory cache and the number of bits to use for the (optional) bloom filter.
These settings, and many others, can be specified as arguments to the
:py:class:`DB` constructor. For this tutorial we'll just use the LevelDB
defaults.

To close the database we just opened, you can just delete the variable that
points to it::

    >>> del db

Note that the remainder of this tutorial assumes an open database, so you
probably want to skip the above line if you're performing all the steps in this
tutorial yourself.


Basic operations
================

Now that we have our database, we can use the basic LevelDB operations: putting,
getting, and deleting data. Let's look at these in turn.

First we'll add some data to the database by calling :py:meth:`DB.put` with a
key/value pair::

    >>> db.put(b'key', b'value')
    >>> db.put(b'another-key', b'another-value')

To get the data out again, use :py:meth:`DB.get`::

    >>> db.get(b'key')
    'value'

If you try to retrieve a key that does not exist, a ``None`` value is returned::

    >>> print(db.get(b'yet-another-key'))
    None

Finally, to delete data from the database, use :py:meth:`DB.delete`::

    >>> db.delete(b'key')
    >>> db.delete(b'another-key')

At this point our database is empty again. Note that, in addition to the basic
use shown above, the :py:meth:`~DB.put`, :py:meth:`~DB.get`, and
:py:meth:`~DB.delete` method accepts optional keyword arguments that influence
their behaviour, e.g. for synchronous writes or reads that will not fill the
cache.


Important note about byte strings
=================================

LevelDB stores all data as uninterpreted *byte strings*. Plyvel works the same
way, and uses Python byte strings for all keys and values stored in and
retrieved from LevelDB databases. In Python 2, this is the `str` type; in Python
3, this is the `bytes` type. Since the default string type for string literals
differs between Python 2 and 3, it is strongly recommended to use an explicit
``b`` prefix for all byte string literals in both Python 2 and Python 3 code,
e.g. ``b'this is a byte string'``. This avoids ambiguity and ensures that your
code keeps working as intended if you switch between Python 2 and Python 3.


Write batches
=============

LevelDB provides *write batches* for bulk data modification. Since batches are
faster than repeatedly calling :py:meth:`DB.put` or :py:meth:`DB.delete`,
batches are perfect for bulk loading data. Let's write some data::

    >>> wb = db.write_batch()
    >>> for i in xrange(100000):
            wb.put(bytes(i), bytes(i) * 100)
    ...
    >>> wb.write()

Since write batches are committed in an atomic way, either the complete batch is
written, or none of it, so if your machine crashes while LevelDB writes the
batch to disk, the database will not end up containing partial or inconsistent
data.

Write batches can also act as context managers. The following code does the same
as the example above, but there is no call to :py:meth:`WriteBatch.write`
anymore:

    >>> with db.write_batch() as wb:
    ...     for i in xrange(100000):
    ...         wb.put(bytes(i), bytes(i) * 100)

If an exception was raised somewhere in your ``with`` block, the values written
to the batch will be saved in the database, so you won't lose previously written
key/value pairs.


Snapshots
=========

A snapshot is a consistent read-only view over the entire database. Any data
that is modified after the snapshot was taken, will not be seen by the snapshot.
Let's store a value:

    >>> db.put(b'key', b'first-value')

Now we'll make a snapshot using :py:meth:`DB.snapshot`::

    >>> sn = db.snapshot()
    >>> sn.get(b'key')
    'first-value'

At this point any modifications to the database will not be visible by the
snapshot::

    >>> db.put(b'key', b'second-value')
    >>> sn.get(b'key')
    'first-value'

Long-lived snapshots may consume significant resources in your LevelDB database,
since the snapshot prevents LevelDB from cleaning up old data that is still
accessible by the snapshot. This means that you should never keep a snapshot
around longer than necessary. The snapshot and its associated resources will be
released automatically when the variable goes out of scope and the garbage
collector comes by to clean it up. Alternatively, you can delete it yourself::

    >>> del sn

Iterators
=========

TODO: this section is yet to be written.


.. rubric:: Next steps

A complete description of the Plyvel API is available from the :doc:`API
reference <api>`. The tutorial above should be enough to get you started though.

.. vim: set spell spelllang=en:
