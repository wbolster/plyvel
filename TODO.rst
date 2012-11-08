
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

  * create_if_missing
  * error_if_exists
  * paranoid_checks
  * write_buffer_size
  * max_open_files
  * block cache (LRU cache size)
  * block_size
  * block_restart_interval
  * compression (None or 'snappy')
  * filter_policy (number of bloom filter bits)

* Wrap DestroyDB
* Wrap RepairDB
* Check if/when iterator.status() should be checked
* Custom errors (extending main Error class) for different error types

Lower priority tasks:

* Custom comparators (if desired at all)
* Wrap DB.GetApproximateSizes()
* Wrap DB.CompactRange
