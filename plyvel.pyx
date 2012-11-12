# cython: embedsignature=True

"""
LevelDB module.

Use LevelDB.DB() to create or open a database.
"""

import sys

cimport cython

from libcpp.string cimport string
from libcpp cimport bool

cimport cpp_leveldb
from cpp_leveldb cimport (
    Cache,
    Comparator,
    DestroyDB,
    NewBloomFilterPolicy,
    NewLRUCache,
    Options,
    ReadOptions,
    RepairDB,
    Slice,
    Status,
    WriteOptions,
)


__leveldb_version__ = '%d.%d' % (cpp_leveldb.kMajorVersion,
                                 cpp_leveldb.kMinorVersion)


#
# Errors and error handling
#

class Error(Exception):
    """Generic LevelDB error.

    This class is also the "parent" error for other LevelDB errors
    (IOError and CorruptionError). Other exceptions from this module
    subclass this class.
    """
    pass


class IOError(Error, IOError):
    """LevelDB IO error

    This class extends both the main LevelDB Error class from this
    module and Python's built-in IOError.
    """
    pass


class CorruptionError(Error):
    """LevelDB corruption error"""
    pass


cdef int raise_for_status(Status st) except -1:
    if st.ok():
        return 0

    if st.IsIOError():
        raise IOError(st.ToString())

    if st.IsCorruption():
        raise CorruptionError(st.ToString())

    # Generic fallback
    raise Error(st.ToString())


#
# Utilities
#

cdef inline db_get(DB db, bytes key, ReadOptions read_options):
    cdef string value
    cdef Status st

    st = db.db.Get(read_options, Slice(key, len(key)), &value)

    if st.IsNotFound():
        return None
    raise_for_status(st)

    return value


cdef bytes to_file_system_name(name):
    if isinstance(name, bytes):
        return name

    if not isinstance(name, unicode):
        raise TypeError(
            "'name' arg must be a byte string or a unicode string")

    encoding = sys.getfilesystemencoding() or 'ascii'
    try:
        return name.encode(encoding)
    except UnicodeEncodeError as exc:
        raise ValueError(
            "Cannot convert unicode 'name' to a file system name: %s" % exc)


#
# Database
#

@cython.final
cdef class DB:
    """LevelDB database.

    A LevelDB database is a persistent ordered map from keys to values.
    """

    cdef cpp_leveldb.DB* db
    cdef Comparator* comparator
    cdef Cache* cache

    def __cinit__(self, name, bool create_if_missing=False,
            bool error_if_exists=False, paranoid_checks=None,
            write_buffer_size=None, max_open_files=None, lru_cache_size=None,
            block_size=None, block_restart_interval=None,
            compression='snappy', int bloom_filter_bits=0):
        """Open the underlying database handle

        :param str name: The name of the database
        """
        cdef Options options
        cdef Status st
        cdef string fsname

        fsname = to_file_system_name(name)

        options = Options()
        options.create_if_missing = create_if_missing
        options.error_if_exists = error_if_exists

        if paranoid_checks is not None:
            options.paranoid_checks = paranoid_checks

        if write_buffer_size is not None:
            options.write_buffer_size = write_buffer_size

        if max_open_files is not None:
            options.max_open_files = max_open_files

        if lru_cache_size is not None:
            self.cache = NewLRUCache(lru_cache_size)
            options.block_cache = self.cache

        if block_size is not None:
            options.block_size = block_size

        if block_restart_interval is not None:
            options.block_restart_interval = block_restart_interval

        if compression is None:
            options.compression = cpp_leveldb.kNoCompression
        else:
            if isinstance(compression, bytes):
                compression = compression.decode('UTF-8')
            if not isinstance(compression, unicode):
                raise TypeError("'compression' must be None or a string")
            if compression == u'snappy':
                options.compression = cpp_leveldb.kSnappyCompression
            else:
                raise ValueError("'compression' must be None or 'snappy'")

        if bloom_filter_bits > 0:
            options.filter_policy = NewBloomFilterPolicy(bloom_filter_bits)

        st = cpp_leveldb.DB_Open(options, fsname, &self.db)
        raise_for_status(st)
        self.comparator = <cpp_leveldb.Comparator*>options.comparator

    def __dealloc__(self):
        del self.db
        if self.cache is not NULL:
            del self.cache

    def get(self, bytes key, *, verify_checksums=None, fill_cache=None):
        """Get the value for specified key (or None if not found)

        :param bytes key:
        :param bool verify_checksums:
        :param bool fill_cache:
        :rtype: bytes
        """
        cdef ReadOptions read_options

        if verify_checksums is not None:
            read_options.verify_checksums = verify_checksums
        if fill_cache is not None:
            read_options.fill_cache = fill_cache

        return db_get(self, key, read_options)

    def put(self, bytes key, bytes value, *, sync=None):
        """Set the value for specified key to the specified value.

        :param bytes key:
        :param bytes value:
        :param bool sync:
        """
        cdef Status st
        cdef WriteOptions write_options = WriteOptions()

        if sync is not None:
            write_options.sync = sync

        st = self.db.Put(
            write_options,
            Slice(key, len(key)),
            Slice(value, len(value)))
        raise_for_status(st)

    def delete(self, bytes key, *, sync=None):
        """Delete the entry for the specified key.

        :param bytes key:
        """
        cdef Status st
        cdef WriteOptions write_options = WriteOptions()

        if sync is not None:
            write_options.sync = sync

        st = self.db.Delete(write_options, Slice(key, len(key)))
        raise_for_status(st)

    def batch(self, *, sync=None):
        return WriteBatch(self, sync=sync)

    def __iter__(self):
        return self.iterator()

    def iterator(self, reverse=False, start=None, stop=None, include_key=True,
            include_value=True, verify_checksums=None, fill_cache=None):
        return Iterator(
            self, reverse=reverse, start=start, stop=stop,
            include_key=include_key, include_value=include_value,
            verify_checksums=verify_checksums, fill_cache=fill_cache,
            snapshot=None)

    def snapshot(self):
        return Snapshot(self)

    def compact_range(self, bytes start=None, bytes stop=None):
        """Compact underlying storage for the specified key range."""
        cdef Slice start_slice
        cdef Slice stop_slice

        if start is not None:
            start_slice = Slice(start, len(start))

        if stop is not None:
            stop_slice = Slice(stop, len(stop))

        self.db.CompactRange(&start_slice, &stop_slice)


def destroy_db(name):
    """Destroy the specified database."""
    # TODO: support Options
    cdef Options options = Options()
    cdef Status st
    cdef string fsname

    fsname = to_file_system_name(name)
    st = DestroyDB(fsname, options)
    raise_for_status(st)


def repair_db(name):
    """Repair the specified database."""
    # TODO: support Options
    cdef Options options = Options()
    cdef Status st
    cdef string fsname

    fsname = to_file_system_name(name)
    st = RepairDB(fsname, options)
    raise_for_status(st)


#
# Write batch
#

cdef class WriteBatch:
    """Write batch for batch put/delete operations.

    Do not instantiate directly; use DB.batch(...) instead.
    """
    cdef cpp_leveldb.WriteBatch* wb
    cdef WriteOptions write_options
    cdef DB db

    def __cinit__(self, DB db not None, *, sync=None):
        self.db = db

        self.write_options = WriteOptions()
        if sync is not None:
            self.write_options.sync = sync

        self.wb = new cpp_leveldb.WriteBatch()

    def __dealloc__(self):
        del self.wb

    def put(self, bytes key, bytes value):
        """Set the value for specified key to the specified value.

        This is like DB.put(), but operates on the write batch instead.
        """
        self.wb.Put(
            Slice(key, len(key)),
            Slice(value, len(value)))

    def delete(self, bytes key):
        """Delete the entry for the specified key.

        This is like DB.delete(), but operates on the write batch
        instead.
        """
        self.wb.Delete(Slice(key, len(key)))

    def clear(self):
        """Clear the batch"""
        self.wb.Clear()

    def write(self):
        """Write the batch to the database"""
        cdef Status st
        st = self.db.db.Write(self.write_options, self.wb)
        raise_for_status(st)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.write()


#
# Iterator
#

cdef enum IteratorState:
    BEFORE_START
    AFTER_STOP
    IN_BETWEEN


cdef enum IteratorDirection:
    FORWARD
    REVERSE


cdef inline int compare(Comparator* comparator, bytes a, bytes b):
    return comparator.Compare(Slice(a, len(a)), Slice(b, len(b)))


cdef class Iterator:
    """Iterator for (ranges of) a database.

    Do not instantiate directly; use DB.iterator(...) or
    Snapshot.iterator() instead.
    """
    cdef DB db
    cdef cpp_leveldb.Iterator* _iter
    cdef IteratorDirection direction
    cdef Slice start
    cdef Slice stop
    cdef bool include_key
    cdef bool include_value
    cdef IteratorState state
    cdef Comparator* comparator

    def __cinit__(self, DB db not None, bool reverse, bytes start, bytes stop,
            bool include_key, bool include_value, bool verify_checksums,
            bool fill_cache, Snapshot snapshot):
        self.db = db
        self.comparator = db.comparator
        self.direction = FORWARD if not reverse else REVERSE
        self.start = Slice(start, len(start)) if start is not None else Slice()
        self.stop = Slice(stop, len(stop)) if stop is not None else Slice()
        self.include_key = include_key
        self.include_value = include_value

        cdef ReadOptions read_options
        if verify_checksums is not None:
            read_options.verify_checksums = verify_checksums
        if fill_cache is not None:
            read_options.fill_cache = fill_cache
        if snapshot is not None:
            read_options.snapshot = snapshot.snapshot

        self._iter = db.db.NewIterator(read_options)
        raise_for_status(self._iter.status())
        self.move_to_start()

    def __dealloc__(self):
        del self._iter

    def __iter__(self):
        return self

    cdef object current(self):
        """Return the current iterator key/value.

        This is an internal helper function that is not exposed in the
        external Python API.
        """
        cdef Slice key_slice
        cdef bytes key
        cdef Slice value_slice
        cdef bytes value
        cdef object out

        # Only build Python strings that will be returned
        if self.include_key:
            key_slice = self._iter.key()
            key = key_slice.data()[:key_slice.size()]
        if self.include_value:
            value_slice = self._iter.value()
            value = value_slice.data()[:value_slice.size()]

        # Build return value
        if self.include_key and self.include_value:
            out = (key, value)
        elif self.include_key:
            out = key
        elif self.include_value:
            out = value
        else:
            out = None

        return out

    def __next__(self):
        """Return the next iterator entry.

        Note: Cython will also create a .next() method that does the
        same as this method.
        """
        if self.direction == FORWARD:
            return self.real_next()
        else:
            return self.real_prev()

    def prev(self):
        """Return the previous iterator entry."""
        if self.direction == FORWARD:
            return self.real_prev()
        else:
            return self.real_next()

    cdef real_next(self):
        if self.state == IN_BETWEEN:
            self._iter.Next()
            if not self._iter.Valid():
                self.state = AFTER_STOP
                raise StopIteration
        elif self.state == BEFORE_START:
            if self.start.empty():
                self._iter.SeekToFirst()
            else:
                self._iter.Seek(self.start)
            if not self._iter.Valid():
                # Iterator is empty
                raise StopIteration
            self.state = IN_BETWEEN
        elif self.state == AFTER_STOP:
            raise StopIteration

        raise_for_status(self._iter.status())

        # Check range boundaries
        if not self.stop.empty() and self.comparator.Compare(
                self._iter.key(), self.stop) >= 0:
            self.state = AFTER_STOP
            raise StopIteration

        return self.current()

    cdef real_prev(self):
        if self.state == IN_BETWEEN:
            pass
        elif self.state == BEFORE_START:
            raise StopIteration
        elif self.state == AFTER_STOP:
            if self.stop.empty():
                # No stop key, seek to last entry
                self._iter.SeekToLast()
                if not self._iter.Valid():
                    # Iterator is empty
                    raise StopIteration
            else:
                # Stop key specified: seek to it and move one step back
                # (since the end of the range is exclusive)
                self._iter.Seek(self.stop)
                if not self._iter.Valid():
                    # Iterator is empty
                    raise StopIteration
                self._iter.Prev()
                if not self._iter.Valid():
                    raise StopIteration

        raise_for_status(self._iter.status())

        out = self.current()
        self._iter.Prev()
        if not self._iter.Valid():
            self.state = BEFORE_START
        elif not self.start.empty() and self.comparator.Compare(
                self._iter.key(), self.start) < 0:
            # Iterator is valid, but has moved before the 'start' key
            self.state = BEFORE_START
        else:
            self.state = IN_BETWEEN

        raise_for_status(self._iter.status())

        return out

    def move_to_start(self):
        """Move the pointer before the start key of the iterator.

        This "rewinds" the iterator, so that it is in the same state as
        when first created. This means calling .next() will return the
        first entry.
        """
        self.state = BEFORE_START if self.direction == FORWARD else AFTER_STOP

    def move_to_stop(self):
        """Move the iterator pointer past the end of the range.

        This "fast-forwards" the iterator past the end. After this call
        the iterator is exhausted, which means a call to .next() raises
        StopIteration, but .prev() will work.
        """
        self.state = AFTER_STOP if self.direction == FORWARD else BEFORE_START

    def seek(self, bytes target):
        # TODO: should this be in the public API?
        self._iter.Seek(Slice(target, len(target)))


#
# Snapshot
#

cdef class Snapshot:
    """Datebase snapshot.

    Do not keep unnecessary references to instances of this class around
    longer than needed, because LevelDB will not release the resources
    required for this snapshot until a snapshot is released.

    Do not instantiate directly; use DB.snapshot(...) instead.
    """
    cdef cpp_leveldb.Snapshot* snapshot
    cdef DB db

    def __cinit__(self, DB db not None):
        self.db = db
        self.snapshot = <cpp_leveldb.Snapshot*>db.db.GetSnapshot()

    def __dealloc__(self):
        self.db.db.ReleaseSnapshot(self.snapshot)

    def get(self, bytes key, *, verify_checksums=None, fill_cache=None):
        cdef ReadOptions read_options
        read_options.snapshot = self.snapshot
        if verify_checksums is not None:
            read_options.verify_checksums = verify_checksums
        if fill_cache is not None:
            read_options.fill_cache = fill_cache

        return db_get(self.db, key, read_options)

    def __iter__(self):
        return self.iterator()

    def iterator(self, reverse=False, start=None, stop=None, include_key=True,
            include_value=True, verify_checksums=None, fill_cache=None):
        return Iterator(
            self.db, reverse=reverse, start=start, stop=stop,
            include_key=include_key, include_value=include_value,
            verify_checksums=verify_checksums, fill_cache=fill_cache,
            snapshot=self)
