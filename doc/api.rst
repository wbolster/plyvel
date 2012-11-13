=============
API reference
=============

.. py:currentmodule:: plyvel

Plyvel exposes the :py:class:`DB` class as the main interface to LevelDB.
Application code should create a :py:class:`DB` and use the appropriate methods
on this instance to create write batches, snapshots, and iterators for that
LevelDB database.

Plyvel's :py:class:`Iterator` is intended to be used like a normal Python
iterator, so you can just use a standard ``for`` loop to iterate over it.
Directly invoking methods on the :py:class:`Iterator` returned by
:py:meth:`DB.iterator` method is only required for additional functionality.

Plyvel uses standard exceptions like ``TypeError`` and ``ValueError`` as much as
poissble. For LevelDB specific errors, Plyvel may raise a few custom exceptions:
:py:class:`Error`, :py:class:`IOError`, and :py:class:`CorruptionError`.

Most of the terminology in the Plyvel API comes straight from the LevelDB API.
See the LevelDB documentation and the LevelDB header files
(``$prefix/include/leveldb/*.h``) for more detailed explanations of all flags
and options.


Database
========

.. py:class:: DB

   LevelDB database

   A LevelDB database is a persistent ordered map from keys to values.


   .. py:method:: __init__(name, create_if_missing=False, error_if_exists=False, paranoid_checks=None, write_buffer_size=None, max_open_files=None, lru_cache_size=None, block_size=None, block_restart_interval=None, compression='snappy', bloom_filter_bits=0)

      Open the underlying database handle

      :param str name: The name of the database


   .. py:method:: get(key, verify_checksums=None, fill_cache=None)

      Get the value for specified key (or None if not found)

      :param bytes key:
      :param bool verify_checksums:
      :param bool fill_cache:
      :rtype: bytes


   .. py:method:: put(key, value, sync=None)

      Set the value for specified key to the specified value.

      :param bytes key:
      :param bytes value:
      :param bool sync:


   .. py:method:: write_batch(sync=None)

      (TODO)


   .. py:method:: iterator(reverse=False, start=None, stop=None, include_key=True, include_value=True, verify_checksums=None, fill_cache=None)

      (TODO)


   .. py:method:: snapshot()

      (TODO)


   .. method: delete(key, sync=None)

      Delete the entry for the specified key.

      :param bytes key:


   .. py:method:: compact_range(start=None, stop=None)

      Compact underlying storage for the specified key range.


Additionally, existing databases can be repaired or destroyed using these module
level functions:

.. function:: repair_db(name)

   Repair the specified database.


.. function:: destroy_db(name)

   Destroy the specified database.


Write batch
===========

.. py:class:: WriteBatch

   Write batch for batch put/delete operations

   Instances of this class can be used as context managers (Python's ``with``
   block). When the ``with`` block terminates, the write batch will
   automatically write itself to the database without an explicit call to
   :py:meth:`WriteBatch.write`.

   Do not instantiate directly; use :py:meth:`DB.write_batch` instead.


   .. py:method:: put(key, value)

      Set the value for specified key to the specified value.

      This is like :py:meth:`DB.put`, but operates on the write batch instead.


   .. py:method:: delete(key)

      Delete the entry for the specified key.

      This is like :py:meth:`DB.delete`, but operates on the write batch
      instead.


   .. py:method:: clear()

      Clear the batch.


   .. py:method:: write()

      Write the batch to the database.


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


   .. py:method:: get(key, verify_checksums=None, fill_cache=None)

      Same as :py:meth:`DB.get`, but operates on the snapshot instead.


   .. py:method:: iterator(reverse=False, start=None, stop=None, include_key=True, include_value=True, verify_checksums=None, fill_cache=None)

      Same as :py:meth:`DB.iterator`, but operates on the snapshot instead.


Iterator
========

.. py:class:: Iterator

   Iterator to iterate over (ranges of) a database

   The next item in the iterator can be obtained using the :py:func:`next`
   built-in or by looping over the iterator using a ``for`` loop.

   Do not instantiate directly; use :py:meth:`DB.iterator` or
   :py:meth:`Snapshot.iterator` instead.


   .. py:method:: prev()

      Move one step back and return the previous entry.


   .. py:method:: seek_to_start()

      Move the pointer before the start key of the iterator.

      This "rewinds" the iterator, so that it is in the same state as when first
      created. This means calling .next() will return the first entry.


   .. py:method:: seek_to_stop()

      Move the iterator pointer past the end of the range.

      This "fast-forwards" the iterator past the end. After this call the
      iterator is exhausted, which means a call to .next() raises StopIteration,
      but .prev() will work.


Errors
======

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


.. vim: set tabstop=3 shiftwidth=3:
