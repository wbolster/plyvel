TODO
====

* Implement explicit Snapshot.release() method since ``del sn`` might not call
  ``__dealloc__`` directly, resulting in unnecessary resource usage.
* Make Snapshot a context manager for use with a ``with`` block (call
  ``.release()`` from its ``__exit__`` method).
