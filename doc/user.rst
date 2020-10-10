==========
User guide
==========

This user guide gives an overview of Plyvel. It covers:

* opening and closing databases,
* storing and retrieving data,
* working with write batches,
* using snapshots,
* iterating over your data,
* using prefixed databases, and
* implementing custom comparators.

Note: this document assumes basic familiarity with LevelDB; visit the `LevelDB
homepage`_ for more information about its features and design.

.. _`LevelDB homepage`: http://code.google.com/p/leveldb/


Getting started
===============

After :doc:`installing Plyvel <installation>`, we can simply import ``plyvel``::

    >>> import plyvel

Let's open a new database by creating a new :py:class:`DB` instance::

    >>> db = plyvel.DB('/tmp/testdb/', create_if_missing=True)

That's all there is to it. At this point ``/tmp/testdb/`` contains a fresh
LevelDB database (assuming the directory did not contain a LevelDB database
already).

For real world applications, you probably want to tweak things like the size of
the memory cache and the number of bits to use for the (optional) bloom filter.
These settings, and many others, can be specified as arguments to the
:py:class:`DB` constructor. For this tutorial we'll just use the LevelDB
defaults.

To close the database we just opened, use :py:meth:`DB.close` and inspect the
``closed`` property::

    >>> db.closed
    False
    >>> db.close()
    >>> db.closed
    True

Alternatively, you can just delete the variable that points to it, but this
might not close the database immediately, e.g. because active iterators are
using it::

    >>> del db

Note that the remainder of this tutorial assumes an open database, so you
probably want to skip the above if you're performing all the steps in this
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

Optionally, you can specify a default value, just like :py:meth:`dict.get`::

    >>> print(db.get(b'yet-another-key', b'default-value'))
    'default-value'

Finally, to delete data from the database, use :py:meth:`DB.delete`::

    >>> db.delete(b'key')
    >>> db.delete(b'another-key')

At this point our database is empty again. Note that, in addition to the basic
use shown above, the :py:meth:`~DB.put`, :py:meth:`~DB.get`, and
:py:meth:`~DB.delete` methods accept optional keyword arguments that influence
their behaviour, e.g. for synchronous writes or reads that will not fill the
cache.


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
   examples above you will still see the ValueError.


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
released automatically when the snapshot reference count drops to zero, which
(for local variables) happens when the variable goes out of scope (or after
you've issued a ``del`` statement). If you want explicit control over the
lifetime of a snapshot, you can also clean it up yourself using
:py:meth:`Snapshot.close`::

    >>> sn.close()

Alternatively, you can use the snapshot as a context manager:

    >>> with db.snapshot() as sn:
    ...     sn.get(b'key')


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

Any combination of `start` and `stop` arguments is possible. For example, to
iterate from a specific start key until the end of the database::

    >>> for key, value in db.iterator(start=b'key-3'):
    ...     print(key)
    ...
    key-3
    key-4
    key-5

By default the start key is *inclusive* and the stop key is *exclusive*. This
matches the behaviour of Python's built-in :py:func:`range` function. If you
want different behaviour, you can use the `include_start` and `include_stop`
arguments::

    >>> for key, value in db.iterator(start=b'key-2', include_start=False,
    ...                               stop=b'key-5', include_stop=True):
    ...     print(key)
    key-3
    key-4
    key-5

Instead of specifying `start` and `stop` keys, you can also specify a `prefix`
for keys. In this case the iterator will only return key/value pairs whose key
starts with the specified prefix. In our example, all keys have the same prefix,
so this will return all key/value pairs:

    >>> for key, value in db.iterator(prefix=b'ke'):
    ...     print(key)
    key-1
    key-2
    key-3
    key-4
    key-5
    >>> for key, value in db.iterator(prefix=b'key-4'):
    ...     print(key)
    key-4

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

In addition to directly iterating over the database, LevelDB also supports
iterating over snapshots using the :py:meth:`Snapshot.iterator` method. This
method works exactly the same as :py:meth:`DB.iterator`, except that it operates
on the snapshot instead of the complete database.

Closing iterators
-----------------

It is generally not required to close an iterator explicitly, since it will be
closed when it goes out of scope (or is garbage collected). However, due to the
way LevelDB is designed, each iterator operates on an implicit database
snapshot, which can be an expensive resource depending on how the database is
used during the iterator's lifetime. The :py:meth:`Iterator.close` method gives
explicit control over when those resources are released::

    >>> it = db.iterator()
    >>> it.close()

Alternatively, to ensure that an iterator is immediately closed after use, you
can also use it as a context manager using the ``with`` statement::

    >>> with db.iterator() as it:
    ...    for k, v in it:
    ...        pass

Non-linear iteration
--------------------

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

Additionally, Plyvel supports seeking on iterators::

    >>> it = db.iterator(include_value=False)
    >>> it.seek(b'key-3')
    >>> next(it)
    'key-3'
    >>> it.seek_to_start()
    >>> next(it)
    'key-1'

See the :py:class:`Iterator` API reference for more information about advanced
iterator usage.

Raw iterators
-------------

In addition to the iterators describe above, which adhere to the Python iterator
protocol, there is also a *raw iterator* API that mimics the C++ iterator API
provided by LevelDB. Since this interface is only intended for advanced use
cases, it is not covered in this user guide. See the API reference for
:py:meth:`DB.raw_iterator` and :py:class:`RawIterator` for more information.


Prefixed databases
==================

LevelDB databases have a single key space. A common way to split a LevelDB
database into separate partitions is to use a prefix for each partition. Plyvel
makes this very easy to do using the :py:meth:`DB.prefixed_db` method:

    >>> my_sub_db = db.prefixed_db(b'example-')

The ``my_sub_db`` variable in this example points to an instance of the
:py:class:`PrefixedDB` class. This class behaves mostly like a normal Plyvel
:py:class:`DB` instance, but all operations will transparently add the key
prefix to all keys that it accepts (e.g. in :py:meth:`PrefixedDB.get`), and
strip the key prefix from all keys that it returns (e.g. from
:py:meth:`PrefixedDB.iterator`). Examples::

    >>> my_sub_db.get(b'some-key')  # this looks up b'example-some-key'
    >>> my_sub_db.put(b'some-key', b'value')  # this sets b'example-some-key'

Almost all functionality available on :py:class:`DB` is also available from
:py:class:`PrefixedDB`: write batches, iterators, snapshots, and also iterators
over snapshots. A :py:class:`PrefixedDB` is simply a lightweight object that
delegates to the the real :py:class:`DB`, which is accessible using the
:py:attr:`~PrefixedDB.db` attribute:

    >>> real_db = my_sub_db.db

You can even nest key spaces by creating prefixed prefixed databases using
:py:meth:`PrefixedDB.prefixed_db`:

    >>> my_sub_sub_db = my_sub_db.prefixed_db(b'other-prefix')


Custom comparators
==================

LevelDB provides an ordered data store, which means all keys are stored in
sorted order. By default, a byte-wise comparator that works like
:c:func:`strcmp()` is used, but this behaviour can be changed by providing a
custom comparator. Plyvel allows you to use a Python callable as a custom
LevelDB comparator.

The signature for a comparator callable is simple: it takes two byte strings and
should return either a positive number, zero, or a negative number, depending on
whether the first byte string is greater than, equal to or less than the second
byte string. (These are the same semantics as the built-in :py:func:`cmp()`,
which has been removed in Python 3 in favour of the so-called ‘rich’ comparison
methods.)

A simple comparator function for case insensitive comparisons might look like
this::

    def comparator(a, b):
        a = a.lower()
        b = b.lower()

        if a < b:
            # a sorts before b
            return -1

        if a > b:
            # a sorts after b
            return 1

        # a and b are equal
        return 0

(This is a toy example. It only works properly for byte strings with characters
in the ASCII range.)

To use this comparator, pass the `comparator` and `comparator_name` arguments to
the :py:class:`DB` constructor::

    >>> db = DB('/path/to/database/',
    ...         comparator=comparator,  # the function defined above
    ...         comparator_name=b'CaseInsensitiveComparator')

The comparator name, which must be a byte string, will be stored in the
database. LevelDB refuses to open existing databases if the provided comparator
name does not match the one in the database.

LevelDB invokes the comparator callable repeatedly during many of its
operations, including storing and retrieving data, but also during background
compactions. Background compaction uses threads that are ‘invisible’ from
Python. This means that custom comparator callables *must not* raise any
exceptions, since there is no proper way to recover from those. If an exception
happens nonetheless, Plyvel will print the traceback to `stderr` and immediately
abort your program to avoid database corruption.

A final thing to keep in mind is that custom comparators written in Python come
with a considerable performance impact. Experiments with simple Python
comparator functions like the example above show a 4× slowdown for bulk writes
compared to the built-in LevelDB comparator.


.. rubric:: Next steps

The user guide should be enough to get you started with Plyvel. A complete
description of the Plyvel API is available from the :doc:`API reference <api>`.

.. vim: set spell spelllang=en:
