# distutils: language = c++

from libc.string cimport const_char
from libcpp cimport bool
from libcpp.string cimport string


cdef extern from "stdint.h":
    # XXX: Assume 64 bit; Cython will use the actual definition from
    # "stdint.h" when compiling
    ctypedef unsigned long long uint64_t


cdef extern from "leveldb/db.h" namespace "leveldb":

    int kMajorVersion
    int kMinorVersion

    cdef cppclass Snapshot:
        pass

    cdef cppclass Range:
        Slice start
        Slice limit
        Range()
        Range(Slice& s, Slice& l)

    cdef cppclass DB:
        Status Put(WriteOptions& options, Slice& key, Slice& value)
        Status Delete(WriteOptions& options, Slice& key)
        Status Write(WriteOptions& options, WriteBatch* updates)
        Status Get(ReadOptions& options, Slice& key, string* value)
        # Iterator* NewIterator(ReadOptions& options)
        Snapshot* GetSnapshot()
        void ReleaseSnapshot(Snapshot* snapshot)
        bool GetProperty(Slice& property, string* value)
        void GetApproximateSizes(Range* range, int n, uint64_t* sizes)
        void CompactRange(Slice* begin, Slice* end)

    # The DB::open() method is static, and hence not a member of the DB
    # class defined above
    Status DB_Open "DB::Open"(Options& options, string& name, DB** dbptr)

    cdef Status DestroyDB(string& name, Options& options)
    cdef Status RepairDB(string& dbname, Options& options)


cdef extern from "leveldb/status.h" namespace "leveldb":

    cdef cppclass Status:
        bool ok()
        bool IsNotFound()
        bool IsCorruption()
        bool IsIOError()
        string ToString()


cdef extern from "leveldb/options.h" namespace "leveldb":

    cdef enum CompressionType:
        kNoCompression
        kSnappyCompression

    cdef cppclass Options:
        # Comparator* comparator
        bool create_if_missing
        bool error_if_exists
        bool paranoid_checks
        # Env* env
        # Logger* info_log
        size_t write_buffer_size
        int max_open_files
        # Cache* block_cache
        size_t block_size
        int block_restart_interval
        CompressionType compression
        # FilterPolicy* filter_policy
        Options()

    cdef cppclass ReadOptions:
        bool verify_checksums
        bool fill_cache
        Snapshot* snapshot
        ReadOptions()

    cdef cppclass WriteOptions:
        bool sync
        WriteOptions()


cdef extern from "leveldb/slice.h" namespace "leveldb":

    cdef cppclass Slice:
        Slice()
        Slice(const_char* d, size_t n)
        Slice(string& s)
        Slice(const_char* s)
        const_char* data()
        size_t size()
        bool empty()
        # char operator[](size_t n)
        void clear()
        void remove_prefix(size_t n)
        string ToString()
        int compare(Slice& b)
        bool starts_with(Slice& x)


cdef extern from "leveldb/write_batch.h" namespace "leveldb":

    cdef cppclass WriteBatch:
        WriteBatch()
        void Put(Slice& key, Slice& value)
        void Delete(Slice& key)
        void Clear()
        # Status Iterate(Handler* handler) const


cdef extern from "leveldb/iterator.h" namespace "leveldb":

    cdef cppclass Iterator:
        Iterator()
        bool Valid()
        void SeekToFirst()
        void SeekToLast()
        void Seek(Slice& target)
        void Next()
        void Prev()
        Slice key()
        Slice value()
        Status status()
        # void RegisterCleanup(CleanupFunction function, void* arg1, void* arg2);
