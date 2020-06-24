=============
API reference
=============

This document is the API reference for Plyvel. It describes all classes,
methods, functions, and attributes that are part of the public API.

Most of the terminology in the Plyvel API comes straight from the LevelDB API.
See the LevelDB documentation and the LevelDB header files
(``$prefix/include/leveldb/*.h``) for more detailed explanations of all flags
and options.


Database
========

Plyvel exposes the :py:class:`DB` class as the main interface to LevelDB.
Application code should create a :py:class:`DB` and use the appropriate methods
on this instance to create write batches, snapshots, and iterators for that
LevelDB database.

.. py:class:: DB

   LevelDB database

   .. py:method:: __init__(name, create_if_missing=False, error_if_exists=False, paranoid_checks=None, write_buffer_size=None, max_open_files=None, lru_cache_size=None, block_size=None, block_restart_interval=None, max_file_size=None, compression='snappy', bloom_filter_bits=0, comparator=None, comparator_name=None)

      Open the underlying database handle.

      Most arguments have the same name as the the corresponding LevelDB
      parameters; see the LevelDB documentation for a detailed description.
      Arguments defaulting to `None` are only propagated to LevelDB if
      specified, e.g. not specifying a `write_buffer_size` means the LevelDB
      defaults are used.

      Most arguments are optional; only the database name is required.

      See the descriptions for :cpp:class:`DB`, :cpp:func:`DB::Open`,
      :cpp:class:`Cache`, :cpp:class:`FilterPolicy`, and :cpp:class:`Comparator`
      in the LevelDB C++ API for more information.

      .. versionadded:: 1.0.0
         `max_file_size` argument

      :param str name: name of the database (directory name)
      :param bool create_if_missing: whether a new database should be created if
                                     needed
      :param bool error_if_exists: whether to raise an exception if the database
                                   already exists
      :param bool paranoid_checks: whether to enable paranoid checks
      :param int write_buffer_size: size of the write buffer (in bytes)
      :param int max_open_files: maximum number of files to keep open
      :param int lru_cache_size: size of the LRU cache (in bytes)
      :param int block_size: block size (in bytes)
      :param int block_restart_interval: block restart interval for delta
                                         encoding of keys
      :param bool max_file_size: maximum file size (in bytes)
      :param bool compression: whether to use Snappy compression (enabled by default))
      :param int bloom_filter_bits: the number of bits to use for a bloom
                                    filter; the default of 0 means that no bloom
                                    filter will be used
      :param callable comparator: a custom comparator callable that takes two
                                  byte strings and returns an integer
      :param bytes comparator_name: name for the custom comparator


   .. py:attribute:: name

      The (directory) name of this :py:class:`DB` instance. This is a
      *read-only* attribute and must be set at instantiation time.

      *New in version 1.1.0.*

   .. py:method:: close()

      Close the database.

      This closes the database and releases associated resources such as open
      file pointers and caches.

      Any further operations on the closed database will raise
      :py:exc:`RuntimeError`.

      .. warning::

         Closing a database while other threads are busy accessing the same
         database may result in hard crashes, since database operations do not
         perform any synchronisation/locking on the database object (for
         performance reasons) and simply assume it is available (and open).
         Applications should make sure not to close databases that are
         concurrently used from other threads.

      See the description for :cpp:class:`DB` in the LevelDB C++ API for more
      information. This method deletes the underlying DB handle in the LevelDB
      C++ API and also frees other related objects.


   .. py:attribute:: closed

      Boolean attribute indicating whether the database is closed.


   .. py:method:: get(key, default=None, verify_checksums=False, fill_cache=True)

      Get the value for the specified key, or `default` if no value was set.

      See the description for :cpp:func:`DB::Get` in the LevelDB C++ API for
      more information.

      .. versionadded:: 0.4
         `default` argument

      :param bytes key: key to retrieve
      :param default: default value if key is not found
      :param bool verify_checksums: whether to verify checksums
      :param bool fill_cache: whether to fill the cache
      :return: value for the specified key, or `None` if not found
      :rtype: bytes


   .. py:method:: put(key, value, sync=False)

      Set a value for the specified key.

      See the description for :cpp:func:`DB::Put` in the LevelDB C++ API for
      more information.

      :param bytes key: key to set
      :param bytes value: value to set
      :param bool sync: whether to use synchronous writes


   .. method:: delete(key, sync=False)

      Delete the key/value pair for the specified key.

      See the description for :cpp:func:`DB::Delete` in the LevelDB C++ API for
      more information.

      :param bytes key: key to delete
      :param bool sync: whether to use synchronous writes


   .. py:method:: write_batch(transaction=False, sync=False)

      Create a new :py:class:`WriteBatch` instance for this database.

      See the :py:class:`WriteBatch` API for more information.

      Note that this method does not write a batch to the database; it only
      creates a new write batch instance.

      :param bool transaction: whether to enable transaction-like behaviour when
                               the batch is used in a ``with`` block
      :param bool sync: whether to use synchronous writes
      :return: new :py:class:`WriteBatch` instance
      :rtype: :py:class:`WriteBatch`


   .. py:method:: iterator(reverse=False, start=None, stop=None, include_start=True, include_stop=False, prefix=None, include_key=True, include_value=True, verify_checksums=False, fill_cache=True)

      Create a new :py:class:`Iterator` instance for this database.

      All arguments are optional, and not all arguments can be used together,
      because some combinations make no sense. In particular:

      * `start` and `stop` cannot be used if a `prefix` is specified.
      * `include_start` and `include_stop` are only used if `start` and `stop`
        are specified.

      Note: due to the whay the `prefix` support is implemented, this feature
      only works reliably when the default DB comparator is used.

      See the :py:class:`Iterator` API for more information about iterators.

      :param bool reverse: whether the iterator should iterate in reverse order
      :param bytes start: the start key (inclusive by default) of the iterator
                          range
      :param bytes stop: the stop key (exclusive by default) of the iterator
                         range
      :param bool include_start: whether to include the start key in the range
      :param bool include_stop: whether to include the stop key in the range
      :param bytes prefix: prefix that all keys in the the range must have
      :param bool include_key: whether to include keys in the returned data
      :param bool include_value: whether to include values in the returned data
      :param bool verify_checksums: whether to verify checksums
      :param bool fill_cache: whether to fill the cache
      :return: new :py:class:`Iterator` instance
      :rtype: :py:class:`Iterator`


   .. py:method:: raw_iterator(verify_checksums=False, fill_cache=True)

      Create a new :py:class:`RawIterator` instance for this database.

      See the :py:class:`RawIterator` API for more information.


   .. py:method:: snapshot()

      Create a new :py:class:`Snapshot` instance for this database.

      See the :py:class:`Snapshot` API for more information.


   .. py:method:: get_property(name)

      Get the specified property from LevelDB.

      This returns the property value or `None` if no value is available.
      Example property name: ``b'leveldb.stats'``.

      See the description for :cpp:func:`DB::GetProperty` in the LevelDB C++ API
      for more information.

      :param bytes name: name of the property
      :return: property value or `None`
      :rtype: bytes


   .. py:method:: compact_range(start=None, stop=None)

      Compact underlying storage for the specified key range.

      See the description for :cpp:func:`DB::CompactRange` in the LevelDB C++
      API for more information.

      :param bytes start: start key of range to compact (optional)
      :param bytes stop: stop key of range to compact (optional)


   .. py:method:: approximate_size(start, stop)

      Return the approximate file system size for the specified range.

      See the description for :cpp:func:`DB::GetApproximateSizes` in the LevelDB
      C++ API for more information.

      :param bytes start: start key of the range
      :param bytes stop: stop key of the range
      :return: approximate size
      :rtype: int


   .. py:method:: approximate_sizes(\*ranges)

      Return the approximate file system sizes for the specified ranges.

      This method takes a variable number of arguments. Each argument denotes a
      range as a `(start, stop)` tuple, where `start` and `stop` are both byte
      strings. Example::

         db.approximate_sizes(
             (b'a-key', b'other-key'),
             (b'some-other-key', b'yet-another-key'))

      See the description for :cpp:func:`DB::GetApproximateSizes` in the LevelDB
      C++ API for more information.

      :param ranges: variable number of `(start, stop`) tuples
      :return: approximate sizes for the specified ranges
      :rtype: list

   .. py:method:: prefixed_db(prefix)

      Return a new :py:class:`PrefixedDB` instance for this database.

      See the :py:class:`PrefixedDB` API for more information.

      :param bytes prefix: prefix to use
      :return: new :py:class:`PrefixedDB` instance
      :rtype: :py:class:`PrefixedDB`


Prefixed database
-----------------

.. py:class:: PrefixedDB

   A :py:class:`DB`-like object that transparently prefixes all database keys.

   Do not instantiate directly; use :py:meth:`DB.prefixed_db` instead.

   .. py:attribute:: prefix

      The prefix used by this :py:class:`PrefixedDB`.

   .. py:attribute:: db

      The underlying :py:class:`DB` instance.

   .. py:method:: get(...)

      See :py:meth:`DB.get`.

   .. py:method:: put(...)

      See :py:meth:`DB.put`.

   .. py:method:: delete(...)

      See :py:meth:`DB.delete`.

   .. py:method:: write_batch(...)

      See :py:meth:`DB.write_batch`.

   .. py:method:: iterator(...)

      See :py:meth:`DB.iterator`.

   .. py:method:: snapshot(...)

      See :py:meth:`DB.snapshot`.

   .. py:method:: prefixed_db(...)

      Create another :py:class:`PrefixedDB` instance with an additional key
      prefix, which will be appended to the prefix used by this
      :py:class:`PrefixedDB` instance.

      See :py:meth:`DB.prefixed_db`.


Database maintenance
--------------------

Existing databases can be repaired or destroyed using these module level
functions:

.. py:function:: repair_db(name, paranoid_checks=None, write_buffer_size=None, max_open_files=None, lru_cache_size=None, block_size=None, block_restart_interval=None, max_file_size=None, compression='snappy', bloom_filter_bits=0, comparator=None, comparator_name=None)

   Repair the specified database.

   See :py:class:`DB` for a description of the arguments.

   See the description for :cpp:func:`RepairDB` in the LevelDB C++ API for more
   information.


.. py:function:: destroy_db(name)

   Destroy the specified database.

   :param str name: name of the database (directory name)

   See the description for :cpp:func:`DestroyDB` in the LevelDB C++ API for more
   information.


Write batch
===========

.. py:class:: WriteBatch

   Write batch for batch put/delete operations

   Instances of this class can be used as context managers (Python's ``with``
   block). When the ``with`` block terminates, the write batch will
   automatically write itself to the database without an explicit call to
   :py:meth:`WriteBatch.write`::

      with db.write_batch() as b:
          b.put(b'key', b'value')

   The `transaction` argument to :py:meth:`DB.write_batch` specifies whether the
   batch should be written after an exception occurred in the ``with`` block. By
   default, the batch is written (this is like a ``try`` statement with a
   ``finally`` clause), but if transaction mode is enabled`, the batch will be
   discarded (this is like a ``try`` statement with an ``else`` clause).

   Note: methods on a :py:class:`WriteBatch` do not take a `sync` argument; this
   flag can be specified for the complete write batch when it is created using
   :py:meth:`DB.write_batch`.

   Do not instantiate directly; use :py:meth:`DB.write_batch` instead.

   See the descriptions for :cpp:class:`WriteBatch` and :cpp:func:`DB::Write` in
   the LevelDB C++ API for more information.


   .. py:method:: put(key, value)

      Set a value for the specified key.

      This is like :py:meth:`DB.put`, but operates on the write batch instead.


   .. py:method:: delete(key)

      Delete the key/value pair for the specified key.

      This is like :py:meth:`DB.delete`, but operates on the write batch
      instead.


   .. py:method:: clear()

      Clear the batch.

      This discards all updates buffered in this write batch.


   .. py:method:: write()

      Write the batch to the associated database. If you use the write batch as
      a context manager (in a ``with`` block), this method will be invoked
      automatically.


Snapshot
========

.. py:class:: Snapshot

   Database snapshot

   A snapshot provides a consistent view over keys and values. After making a
   snapshot, puts and deletes on the database will not be visible by the
   snapshot.

   Do not keep unnecessary references to instances of this class around longer
   than needed, because LevelDB will not release the resources required for this
   snapshot until a snapshot is released.

   Do not instantiate directly; use :py:meth:`DB.snapshot` instead.

   See the descriptions for :cpp:func:`DB::GetSnapshot` and
   :cpp:func:`DB::ReleaseSnapshot` in the LevelDB C++ API for more information.


   .. py:method:: get(...)

      Get the value for the specified key, or `None` if no value was set.

      Same as :py:meth:`DB.get`, but operates on the snapshot instead.


   .. py:method:: iterator(...)

      Create a new :py:class:`Iterator` instance for this snapshot.

      Same as :py:meth:`DB.iterator`, but operates on the snapshot instead.


   .. py:method:: raw_iterator(...)

      Create a new :py:class:`RawIterator` instance for this snapshot.

      Same as :py:meth:`DB.raw_iterator`, but operates on the snapshot instead.


   .. py:method:: close()

      Close the snapshot. Can also be accomplished using a context manager. See
      :py:meth:`Iterator.close` for an example.

      .. versionadded:: 0.8


   .. py:method:: release()

      Alias for :py:meth:`Snapshot.close`. *Release* is the terminology used in
      the LevelDB C++ API.

      .. versionadded:: 0.8


Iterator
========

Regular iterators
-----------------

Plyvel's :py:class:`Iterator` is intended to be used like a normal Python
iterator, so you can just use a standard ``for`` loop to iterate over it.
Directly invoking methods on the :py:class:`Iterator` returned by
:py:meth:`DB.iterator` method is only required for additional functionality.

.. py:class:: Iterator

   Iterator to iterate over (ranges of) a database

   The next item in the iterator can be obtained using the :py:func:`next`
   built-in or by looping over the iterator using a ``for`` loop.

   Do not instantiate directly; use :py:meth:`DB.iterator` or
   :py:meth:`Snapshot.iterator` instead.

   See the descriptions for :cpp:func:`DB::NewIterator` and
   :cpp:class:`Iterator` in the LevelDB C++ API for more information.


   .. py:method:: prev()

      Move one step back and return the previous entry.

      This returns the same value as the most recent :py:func:`next` call (if
      any).


   .. py:method:: seek_to_start()

      Move the iterator to the start key (or the begin).

      This "rewinds" the iterator, so that it is in the same state as when first
      created. This means calling :py:func:`next` afterwards will return the
      first entry.


   .. py:method:: seek_to_stop()

      Move the iterator to the stop key (or the end).

      This "fast-forwards" the iterator past the end. After this call the
      iterator is exhausted, which means a call to :py:func:`next` raises
      StopIteration, but :py:meth:`~Iterator.prev` will work.


   .. py:method:: seek(target)

      Move the iterator to the specified `target`.

      This moves the iterator to the the first key that sorts equal or after
      the specified `target` within the iterator range (`start` and `stop`).

   .. py:method:: close()

      Close the iterator.

      This closes the iterator and releases the associated resources. Any
      further operations on the closed iterator will raise
      :py:exc:`RuntimeError`.

      To automatically close an iterator, a context manager can be used::

          with db.iterator() as it:
              for k, v in it:
                  pass  # do something

          it.seek_to_start()  # raises RuntimeError

      .. versionadded:: 0.6

Raw iterators
-------------

The raw iteration API mimics the C++ iterator interface provided by LevelDB.
See the LevelDB documentation for a detailed description.

.. py:class:: RawIterator

   Raw iterator to iterate over a database

   .. versionadded:: 0.7

   .. py:method:: valid()

      Check whether the iterator is currently valid.

   .. py:method:: seek_to_first()

      Seek to the first key (if any).

   .. py:method:: seek_to_last()

      Seek to the last key (if any).

   .. py:method:: seek(target)

      Seek to or past the specified key (if any).

   .. py:method:: next()

      Move the iterator one step forward.

      May raise :py:exc:`IteratorInvalidError`.

   .. py:method:: prev()

      Move the iterator one step backward.

      May raise :py:exc:`IteratorInvalidError`.

   .. py:method:: key()

      Return the current key.

      May raise :py:exc:`IteratorInvalidError`.

   .. py:method:: value()

      Return the current value.

      May raise :py:exc:`IteratorInvalidError`.

   .. py:method:: item()

      Return the current key and value as a tuple.

      May raise :py:exc:`IteratorInvalidError`.

   .. py:method:: close()

      Close the iterator. Can also be accomplished using a context manager.
      See :py:meth:`Iterator.close`.


Errors
======

Plyvel uses standard exceptions like ``TypeError``, ``ValueError``, and
``RuntimeError`` as much as possible. For LevelDB specific errors, Plyvel may
raise a few custom exceptions, which are described below.

.. py:exception:: Error

   Generic LevelDB error

   This class is also the "parent" error for other LevelDB errors
   (:py:exc:`IOError` and :py:exc:`CorruptionError`). Other exceptions from this
   module extend from this class.


.. py:exception:: IOError

   LevelDB IO error

   This class extends both the main LevelDB Error class from this
   module and Python's built-in IOError.


.. py:exception:: CorruptionError

   LevelDB corruption error


.. py:exception:: IteratorInvalidError

   Used by :py:class:`RawIterator` to signal invalid iterator state.


.. vim: set tabstop=3 shiftwidth=3:
