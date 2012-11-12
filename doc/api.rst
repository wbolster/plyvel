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

.. autoclass:: plyvel.DB

Additionally, existing databases can be repaired or destroyed using these module
level functions:

.. autofunction:: plyvel.repair_db
.. autofunction:: plyvel.destroy_db


Write batch
===========

.. autoclass:: plyvel.WriteBatch


Snapshot
========

.. autoclass:: plyvel.Snapshot


Iterator
========

.. autoclass:: plyvel.Iterator


Errors
======

.. autoclass:: plyvel.Error
.. autoclass:: plyvel.IOError
.. autoclass:: plyvel.CorruptionError
