
cimport cython
from libcpp.string cimport string

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

    def delete(self, bytes key):
        """Delete the entry for the specified key.

        :param bytes key:
        """
        cdef Status st
        st = self.db.Delete(WriteOptions(), Slice(key, len(key)))
        raise_for_status(st)

    def batch(self):
        return WriteBatch(db=self)

    def __iter__(self):
        raise NotImplementedError()


cdef class WriteBatch:
    cdef cpp_leveldb.DB* db
    cdef cpp_leveldb.WriteBatch* wb

    def __cinit__(self, DB db not None):
        self.db = db.db
        self.wb = new cpp_leveldb.WriteBatch()

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
        # TODO: handle WriteOptions
        cdef Status st
        st = self.db.Write(WriteOptions(), self.wb)
        raise_for_status(st)
