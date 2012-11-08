
TODO
====

Required before this library is to be taken seriously:

* Seeking to (or before) specific keys in iterators
* Decent error handling when opening a database fails
* Decent packaging/releasing (setup.py)
* Decide on a license
* Documentation

  * Installation instructions
  * Simple use

* Option handling when opening databases:

  * block cache (LRU cache size)
  * compression (None or 'snappy')

Lower priority tasks:

* Custom comparators (if desired at all)
* Wrap DB.GetApproximateSizes()
