===============
Version history
===============

Plyvel 1.3.0
============

Release date: 2020-10-10

* Use manylinux2010 instead of manylinux1 to build wheels
  (`pr #103 <https://github.com/wbolster/plyvel/pull/103>`_)

* Add Python 3.9 support

* Drop Python 3.5 support

* Completely drop Python 2 support

Plyvel 1.2.0
============

Release date: 2020-01-22

* Add Python 3.8 support
  (`pr #109 <https://github.com/wbolster/plyvel/pull/109>`_)

* Drop Python 3.4 support
  (`pr #109 <https://github.com/wbolster/plyvel/pull/109>`_)

* Build Linux wheels against Snappy 1.1.8, LevelDB 1.22, and produce Python 3.8 wheels
  (`issue #108 <https://github.com/wbolster/plyvel/issues/108>`_,
  `pr #111 <https://github.com/wbolster/plyvel/pull/111>`_, )

* Improve compilation flags for Darwin (OSX) builds
  (`pr #107 <https://github.com/wbolster/plyvel/pull/107>`_)

Plyvel 1.1.0
============

Release date: 2019-05-02

* Expose :py:attr:`~DB.name` attribute to Python code
  (`pr #90 <https://github.com/wbolster/plyvel/pull/90>`_)

* Fix building sources on OSX.
  (`issue #95 <https://github.com/wbolster/plyvel/issues/95>`_,
  `pr #97 <https://github.com/wbolster/plyvel/pull/97>`_)

* Build Linux wheels against LevelDB 1.21


Plyvel 1.0.5
============

Release date: 2018-07-17

* Rebuild wheels: build against Snappy 1.1.7, and produce Python 3.7 wheels
  (`issue #78 <https://github.com/wbolster/plyvel/issues/78>`_,
  `pr #79 <https://github.com/wbolster/plyvel/pull/79>`_)


Plyvel 1.0.4
============

Release date: 2018-01-17

* Build Python wheels with Snappy compression support.
  (`issue #68 <https://github.com/wbolster/plyvel/issues/68>`_)


Plyvel 1.0.3
============

Release date: 2018-01-16

* Fix building sources on OSX.
  (`issue #66 <https://github.com/wbolster/plyvel/issues/66>`_,
  `pr #67 <https://github.com/wbolster/plyvel/issues/67>`_)


Plyvel 1.0.2
============

Release date: 2018-01-12

* Correctly build wide unicode Python 2.7 wheels (cp27-cp27mu, UCS4).
  (`issue #65 <https://github.com/wbolster/plyvel/issues/65>`_)


Plyvel 1.0.1
============

Release date: 2018-01-05

* Provide binary packages (manylinux1 wheels) for Linux.

  These wheel packages have the LevelDB library embedded. This should
  make installation on many Linux systems easier since these packages
  do not depend on a recent LevelDB version being installed
  system-wide: running ``pip install`` will simply download and
  install the extension, instead of compiling it.
  (`pr #64 <https://github.com/wbolster/plyvel/pull/64>`_,
  `issue #62 <https://github.com/wbolster/plyvel/issues/62>`_,
  `issue #63 <https://github.com/wbolster/plyvel/issues/63>`_)


Plyvel 1.0.0
============

Release date: 2018-01-03

* First 1.x release. This library is quite mature, so there is no reason to keep
  using 0.x version numbers. While at it, switch to semantic versioning.

* Drop support for older Python versions. Minimum versions are now Python 3.4+
  for modern Python and Python 2.7+ for legacy Python.

* The mimimum LevelDB version is now 1.20, which added an option for
  the maximum file size, which is now exposed in Plyvel.
  (`pr #61 <https://github.com/wbolster/plyvel/pull/61>`_)

* The various ``.put()`` methods are no longer restricted to just `bytes` (`str`
  in Python 2), but will accept any type implementing Python's buffer protocol,
  such as `bytes`, `bytearray`, and `memoryview`. Note that this only applies to
  values; keys must still be `bytes`.
  (`issue #52 <https://github.com/wbolster/plyvel/issues/52>`_)


Plyvel 0.9
==========

Release date: 2014-08-27

* Ensure that the Python GIL is initialized when a custom comparator is used,
  since the background thread LevelDB uses for compaction calls back into Python
  code in that case. This makes single-threaded programs using a custom
  comparator work as intended. (`issue #35
  <https://github.com/wbolster/plyvel/issues/35>`_)


Plyvel 0.8
==========

Release date: 2013-11-29

* Allow snapshots to be closed explicitly using either
  :py:meth:`Snapshot.close()` or a ``with`` block (`issue #21
  <https://github.com/wbolster/plyvel/issues/21>`_)


Plyvel 0.7
==========

Release date: 2013-11-15

* New raw iterator API that mimics the LevelDB C++ interface. See
  :py:meth:`DB.raw_iterator()` and :py:class:`RawIterator`. (`issue #17
  <https://github.com/wbolster/plyvel/issues/17>`_)

* Migrate to `pytest` and `tox` for testing (`issue #24
  <https://github.com/wbolster/plyvel/issues/24>`_)

* Performance improvements in iterator and write batch construction. The
  internal calls within Plyvel are now a bit faster, and the `weakref` handling
  required for iterators is now a lot faster due to replacing
  :py:class:`weakref.WeakValueDictionary` with manual `weakref` handling.

* The `fill_cache`, `verify_checksums`, and `sync` arguments to various methods
  are now correctly taken into account everywhere, and their default values are
  now booleans reflecting the the LevelDB defaults.


Plyvel 0.6
==========

Release date: 2013-10-18

* Allow iterators to be closed explicitly using either
  :py:meth:`Iterator.close()` or a ``with`` block (`issue #19
  <https://github.com/wbolster/plyvel/issues/19>`_)

* Add useful ``__repr__()`` for :py:class:`DB` and :py:class:`PrefixedDB`
  instances (`issue #16 <https://github.com/wbolster/plyvel/issues/16>`_)


Plyvel 0.5
==========

Release date: 2013-09-17

* Fix :py:meth:`Iterator.seek()` for :py:class:`PrefixedDB` iterators
  (`issue #15 <https://github.com/wbolster/plyvel/issues/15>`_)

* Make some argument type checking a bit stricter (mostly ``None`` checks)

* Support LRU caches larger than 2GB by using the right integer type for the
  ``lru_cache_size`` :py:class:`DB` constructor argument.

* Documentation improvements


Plyvel 0.4
==========

Release date: 2013-06-17

* Add optional 'default' argument for all ``.get()`` methods
  (`issue #11 <https://github.com/wbolster/plyvel/issues/11>`_)


Plyvel 0.3
==========

Release date: 2013-06-03

* Fix iterator behaviour for reverse iterators using a prefix
  (`issue #9 <https://github.com/wbolster/plyvel/issues/9>`_)

* Documentation improvements


Plyvel 0.2
==========

Release date: 2013-03-15

* Fix iterator behaviour for iterators using non-existing start or stop keys
  (`issue #4 <https://github.com/wbolster/plyvel/issues/4>`_)


Plyvel 0.1
==========

Release date: 2012-11-26

* Initial release
