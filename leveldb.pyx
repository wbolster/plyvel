
from libcpp.string cimport string

cimport leveldb

__version__ = '%d.%d' % (leveldb.kMajorVersion, leveldb.kMinorVersion)


cdef class LevelDB:
    """LevelDB database

    A LevelDB database is a persistent ordered map from keys to values.
    """

    cdef leveldb.DB *db

    def __cinit__(self, str directory):
        """Open the underlying database handle

        :param str directory: The database directory
        """
        raise NotImplementedError()

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
