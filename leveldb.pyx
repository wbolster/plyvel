
cimport leveldb

__version__ = '%d.%d' % (leveldb.kMajorVersion, leveldb.kMinorVersion)


class Error(Exception):
    pass


cdef raise_for_status(leveldb.Status st):
    # TODO: add different error classes, depending on the error type
    if not st.ok():
        raise Error(st.ToString())


cdef class LevelDB:
    """LevelDB database

    A LevelDB database is a persistent ordered map from keys to values.
    """

    cdef leveldb.DB* db

    def __cinit__(self, bytes name):
        """Open the underlying database handle

        :param str name: The name of the database
        """
        cdef leveldb.Options options
        cdef leveldb.Status st

        options.create_if_missing = True
        st = leveldb.DB_Open(options, name, &self.db)
        raise_for_status(st)

    def __dealloc__(self):
        del self.db

    def get(self, bytes key):
        cdef Status st
        cdef string value

        st = self.db.Get(ReadOptions(), Slice(key, len(key)), &value)
        if st.IsNotFound():
            return None

        raise_for_status(st)
        return value

    def put(self, bytes key, bytes value):
        cdef Status st
        cdef WriteOptions write_options = WriteOptions()
        st = self.db.Put(write_options,
                         Slice(key, len(key)),
                         Slice(value, len(value)))
        raise_for_status(st)

    def delete(self, bytes key):
        raise NotImplementedError()

    def __iter__(self):
        raise NotImplementedError()
