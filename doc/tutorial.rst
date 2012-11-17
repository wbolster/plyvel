========
Tutorial
========

.. py:currentmodule:: plyvel

This tutorial gives an overview of Plyvel. It covers opening and closing
databases, storing and retrieving data, working with write batches, using
snapshots, and iterating over your data.

Note: this tutorial assumes basic familiarity with LevelDB; visit the `LevelDB
homepage`_ for more information about its features and design.

.. _`LevelDB homepage`: http://code.google.com/p/leveldb/


Getting started
===============

After :doc:`installing Plyvel <installation>`, we can simply import the
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
written, or not at all, so if your machine crashes while LevelDB writes the
batch to disk, the database will not end up containing partial or inconsistent
data. This makes write batches very useful for multiple modifications to the
database that should be applied as a group.

Write batches can also act as context managers. The following code does the same
as the example above, but there is no call to :py:meth:`WriteBatch.write`
anymore:

    >>> with db.write_batch() as wb:
    ...     for i in xrange(100000):
    ...         wb.put(bytes(i), bytes(i) * 100)

If the ``with`` block raises an exception, pending modifications in the write
batch will still be written to the database. This means each modification using
:py:meth:`~WriteBatch.put` or :py:meth:`~WriteBatch.delete` that happened before
the exception was raised will be applied to the database::

    >>> with db.write_batch() as wb:
    ...     wb.put(b'key-1', b'value-1')
    ...     raise ValueError("Something went wrong!")
    ...     wb.put(b'key-2', b'value-2')

At this point the database contains ``key-1``, but not ``key-2``. Sometimes this
behaviour is undesirable. If you want to discard all pending modifications in
the write batch if an exception occurs, you can simply set the `transaction`
argument::

    >>> with db.write_batch(transaction=True) as wb:
    ...     wb.put(b'key-3', b'value-3')
    ...     raise ValueError("Something went wrong!")
    ...     wb.put(b'key-4', b'value-4')

In this case the database will not be modified, because the ``with`` block
raised an exception. In this example this means that neither ``key-3`` nor
``key-4`` will be saved.

.. note::

   Write batches will never silently suppress exceptions. Exceptions will be
   propagated regardless of the value of the `transaction` argument, so in the
   examples above will you will still see the ValueError.


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

All key/value pairs in a LevelDB database will be sorted by key. Because of
this, data can be efficiently retrieved in sorted order. This is what iterators
are for. Iterators allow you to efficiently iterate over all sorted key/value
pairs in the database, or more likely, a range of the database.

Let's fill the database with some data first:

    >>> db.put(b'key-1', b'value-1')
    >>> db.put(b'key-5', b'value-5')
    >>> db.put(b'key-3', b'value-3')
    >>> db.put(b'key-2', b'value-2')
    >>> db.put(b'key-4', b'value-4')

Now we can iterate over all data using a simple ``for`` loop, which will return
all key/value pairs in lexicographical key order::

    >>> for key, value in db:
    ...     print(key)
    ...     print(value)
    ...
    key-1
    value-1
    key-2
    value-2
    key-3
    value-3
    key-4
    value-4
    key-5

While the complete database can be iterated over by just looping over the
:py:class:`DB` instance, this is generally not useful. The
:py:meth:`DB.iterator` method allows you to obtain more specific iterators. This
method takes several optional arguments to specify how the iterator should
behave.

Iterating over a key range
--------------------------

Limiting the range of values that you want the iterator to iterate over can be
achieved by supplying `start` and/or `stop` arguments::

    >>> for key, value in db.iterator(start=b'key-2', stop=b'key-4'):
    ...     print(key)
    ...
    key-2
    key-3

.. note::

   Keep in mind that the start key is *inclusive* and the stop key is
   *exclusive*. This is also how the Python built-in :py:func:`range` function
   works.

Any combination of `start` and `stop` arguments is possible. For example, to
iterate from a specific start key until the end of the database::

    >>> for key, value in db.iterator(start=b'key-3'):
    ...     print(key)
    ...
    key-3
    key-4
    key-5

Limiting the returned data
--------------------------

If you're only interested in either the key or the value, you can use the
`include_key` and `include_value` arguments to omit data you don't need::

    >>> list(db.iterator(start=b'key-2', stop=b'key-4', include_value=False))
    ['key-2', 'key-3']
    >>> list(db.iterator(start=b'key-2', stop=b'key-4', include_key=False))
    ['value-2', 'value-3']

Only requesting the data that you are interested in results in slightly faster
iterators, since Plyvel will avoid unnecessary memory copies and object
construction in this case.

Iterating in reverse order
--------------------------

LevelDB also supports reverse iteration. Just set the `reverse` argument to
`True` to obtain a reverse iterator::

    >>> list(db.iterator(start=b'key-2', stop=b'key-4', include_value=False, reverse=True))
    ['key-3', 'key-2']

Note that the `start` and `stop` keys are the same; the only difference is the
`reverse` argument.

Iterating over snapshots
------------------------

LevelDB also supports iterating over snapshots using the
:py:meth:`Snapshot.iterator` method. This method works exactly the same as
:py:meth:`DB.iterator`, except that it operates on the snapshot instead of the
complete database.

Advanced iterator usage
-----------------------

In the examples above, we've only used Python's standard iteration methods using
a ``for`` loop and the :py:func:`list` constructor. This suffices for most
applications, but sometimes more advanced iterator tricks can be useful. Plyvel
exposes pretty much all features of the LevelDB iterators using extra functions
on the :py:class:`Iterator` instance that :py:meth:`DB.iterator` and
:py:meth:`Snapshot.iterator` returns.

For instance, you can step forward and backward over the same iterator. For
forward stepping, Python's standard :py:func:`next` built-in function can be
used (this is also what a standard ``for`` loop does). For backward stepping,
you will need to call the :py:meth:`~Iterator.prev()` method on the iterator::

    >>> it = db.iterator(include_value=False)
    >>> next(it)
    'key-1'
    >>> next(it)
    'key-2'
    >>> next(it)
    'key-3'
    >>> it.prev()
    'key-3'
    >>> next(it)
    'key-3'
    >>> next(it)
    'key-4'
    >>> next(it)
    'key-5'
    >>> next(it)
    Traceback (most recent call last):
      ...
    StopIteration

    >>> it.prev()
    'key-5'

Note that for reverse iterators, the definition of 'forward' and 'backward' is
inverted, i.e. calling ``next(it)`` on a reverse iterator will return the key
that sorts *before* the key that was most recently returned.

Additionally, Plyvel supports seeking on iterators. See the :py:class:`Iterator`
API reference for more information about advanced iterator usage.


.. rubric:: Next steps

A complete description of the Plyvel API is available from the :doc:`API
reference <api>`. The tutorial above should be enough to get you started though.

.. vim: set spell spelllang=en:
