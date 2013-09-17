===============
Version history
===============


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
