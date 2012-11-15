"""
Plyvel, a fast and feature-rich Python interface to LevelDB.
"""

# Only import the symbols that are part of the public API
from plyvel._plyvel import (
    __leveldb_version__,
    DB,
    repair_db,
    destroy_db,
    Error,
    IOError,
    CorruptionError,
)
