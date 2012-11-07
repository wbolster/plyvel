
cimport cython

from libcpp.string cimport string
from libcpp cimport bool

cimport cpp_leveldb
from cpp_leveldb cimport (Options, ReadOptions, Slice, Status, WriteOptions)


__leveldb_version__ = '%d.%d' % (cpp_leveldb.kMajorVersion,
                                 cpp_leveldb.kMinorVersion)


class Error(Exception):
    pass


cdef void raise_for_status(Status st):
    # TODO: add different error classes, depending on the error type
    if not st.ok():
        raise Error(st.ToString())


cdef enum IteratorState:
    BEFORE_START
    AFTER_STOP
    IN_BETWEEN


@cython.final
cdef class DB:
    """LevelDB database

    A LevelDB database is a persistent ordered map from keys to values.
    """

    cdef cpp_leveldb.DB* db

    def __cinit__(self, bytes name):
        """Open the underlying database handle

        :param str name: The name of the database
        """
        cdef Options options
        cdef Status st

        options.create_if_missing = True
        st = cpp_leveldb.DB_Open(options, name, &self.db)
        raise_for_status(st)

    def __dealloc__(self):
        del self.db

    #
    # Basic operations
    #

    def get(self, bytes key, *, verify_checksums=None, fill_cache=None):
        """Get the value for specified key (or None if not found)

        :param bytes key:
        :param bool verify_checksums:
        :param bool fill_cache:
        :rtype: bytes
        """
        cdef ReadOptions read_options
        cdef Status st
        cdef string value

        if verify_checksums is not None:
            read_options.verify_checksums = verify_checksums

        if fill_cache is not None:
            read_options.fill_cache = fill_cache

        st = self.db.Get(read_options, Slice(key, len(key)), &value)
        if st.IsNotFound():
            return None

        raise_for_status(st)
        return value

    def put(self, bytes key, bytes value, *, sync=None):
        """Set the value for specified key to the specified value.

        :param bytes key:
        :param bytes value:
        :param bool sync:
        """

        cdef Status st
        cdef WriteOptions write_options

        if sync is not None:
            write_options.sync = sync

        st = self.db.Put(write_options,
                         Slice(key, len(key)),
                         Slice(value, len(value)))
        raise_for_status(st)

    def delete(self, bytes key, *, sync=None):
        """Delete the entry for the specified key.

        :param bytes key:
        """
        cdef Status st
        cdef WriteOptions write_options

        if sync is not None:
            write_options.sync = sync

        st = self.db.Delete(write_options, Slice(key, len(key)))
        raise_for_status(st)

    #
    # Batch writes
    #

    def batch(self, *, sync=None):
        return WriteBatch(self, sync=sync)

    #
    # Iteration
    #

    def __iter__(self):
        return self.iterator()

    def iterator(self, reverse=False, start=None, stop=None, include_key=True,
            include_value=True, verify_checksums=None, fill_cache=None):
        return Iterator(self, reverse=reverse, start=start, stop=stop,
                        include_key=include_key, include_value=include_value,
                        verify_checksums=verify_checksums,
                        fill_cache=fill_cache)


cdef class WriteBatch:
    cdef cpp_leveldb.WriteBatch* wb
    cdef WriteOptions write_options
    cdef DB db

    def __cinit__(self, DB db not None, *, sync=None):
        self.db = db

        if sync is not None:
            self.write_options.sync = sync

        self.wb = new cpp_leveldb.WriteBatch()

    def __dealloc__(self):
        del self.wb

    def put(self, bytes key, bytes value):
        """Set the value for specified key to the specified value.

        See DB.put()
        """
        self.wb.Put(
            Slice(key, len(key)),
            Slice(value, len(value)))

    def delete(self, bytes key):
        """Delete the entry for the specified key.

        See DB.delete()
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


cdef class Iterator:
    cdef DB db
    cdef cpp_leveldb.Iterator* _iter
    cdef bool reverse
    cdef bool include_key
    cdef bool include_value
    cdef IteratorState state

    def __cinit__(self, DB db not None, reverse=False, start=None, stop=None,
            include_key=True, include_value=True, verify_checksums=None,
            fill_cache=None):
        cdef ReadOptions read_options

        self.db = db
        self.reverse = reverse
        self.include_key = include_key
        self.include_value = include_value

        # TODO: args type checking

        if verify_checksums is not None:
            read_options.verify_checksums = verify_checksums

        if fill_cache is not None:
            read_options.fill_cache = fill_cache

        self._iter = db.db.NewIterator(read_options)
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
        if self.reverse:
            return self.real_prev()
        else:
            return self.real_next()

    def prev(self):
        """Return the previous iterator entry."""
        if self.reverse:
            return self.real_next()
        else:
            return self.real_prev()

    cdef real_next(self):
        if self.state == IN_BETWEEN:
            self._iter.Next()
            if not self._iter.Valid():
                self.state = AFTER_STOP
                raise StopIteration
            return self.current()

        elif self.state == BEFORE_START:
            self._iter.SeekToFirst()
            if not self._iter.Valid():
                # Iterator is empty
                raise StopIteration
            self.state = IN_BETWEEN
            return self.current()

        assert self.state == AFTER_STOP
        raise StopIteration

    cdef real_prev(self):
        if self.state == BEFORE_START:
            raise StopIteration

        if self.state == AFTER_STOP:
            self._iter.SeekToLast()
            if not self._iter.Valid():
                # Iterator is empty
                raise StopIteration

        out = self.current()
        self._iter.Prev()
        if not self._iter.Valid():
            self.state = BEFORE_START
        else:
            self.state = IN_BETWEEN
        return out

    def move_to_start(self):
        """Move the pointer before the start key of the iterator.

        This "rewinds" the iterator, so that it is in the same state as
        when first created. This means calling .next() will return the
        first entry.
        """
        if self.reverse:
            self.state = AFTER_STOP
        else:
            self.state = BEFORE_START

    def move_to_stop(self):
        """Move the iterator pointer past the end of the range.

        This "fast-forwards" the iterator past the end. After this call
        the iterator is exhausted, which means a call to .next() raises
        StopIteration, but .prev() will work.
        """
        if self.reverse:
            self.state = BEFORE_START
        else:
            self.state = AFTER_STOP

    def seek(self, bytes target):
        self._iter.Seek(Slice(target, len(target)))
