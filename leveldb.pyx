
from libcpp.string cimport string

cimport leveldb

__version__ = '%d.%d' % (leveldb.kMajorVersion, leveldb.kMinorVersion)


class Error(Exception):
    pass


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

        if not st.ok():
            raise Error(st.ToString())

    def __dealloc__(self):
        del self.db

    def get(self, bytes key):
        raise NotImplementedError()

    def put(self, bytes key, bytes value):
        raise NotImplementedError()

    def delete(self, bytes key):
        raise NotImplementedError()

    def __iter__(self):
        raise NotImplementedError()
