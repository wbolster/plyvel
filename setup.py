from os.path import join, dirname
from setuptools import setup
from setuptools.extension import Extension

CURRENT_DIR = dirname(__file__)

with open(join(CURRENT_DIR, 'plyvel/_version.py')) as fp:
    exec(fp.read(), globals(), locals())


def get_file_contents(filename):
    with open(join(CURRENT_DIR, filename)) as fp:
        return fp.read()


plyvel_sources = [
    'plyvel/_plyvel.cpp',
    'plyvel/comparator.cpp',
]
leveldb_sources = [
    'leveldb/db/builder.cc',
    'leveldb/db/c.cc',
    'leveldb/db/db_impl.cc',
    'leveldb/db/db_iter.cc',
    'leveldb/db/dbformat.cc',
    'leveldb/db/dumpfile.cc',
    'leveldb/db/filename.cc',
    'leveldb/db/log_reader.cc',
    'leveldb/db/log_writer.cc',
    'leveldb/db/memtable.cc',
    'leveldb/db/repair.cc',
    'leveldb/db/table_cache.cc',
    'leveldb/db/version_edit.cc',
    'leveldb/db/version_set.cc',
    'leveldb/db/write_batch.cc',
    'leveldb/port/port_posix.cc',
    'leveldb/port/port_posix_sse.cc',
    'leveldb/table/block.cc',
    'leveldb/table/block_builder.cc',
    'leveldb/table/filter_block.cc',
    'leveldb/table/format.cc',
    'leveldb/table/iterator.cc',
    'leveldb/table/merger.cc',
    'leveldb/table/table.cc',
    'leveldb/table/table_builder.cc',
    'leveldb/table/two_level_iterator.cc',
    'leveldb/util/arena.cc',
    'leveldb/util/bloom.cc',
    'leveldb/util/cache.cc',
    'leveldb/util/coding.cc',
    'leveldb/util/comparator.cc',
    'leveldb/util/crc32c.cc',
    'leveldb/util/env.cc',
    'leveldb/util/env_posix.cc',
    'leveldb/util/filter_policy.cc',
    'leveldb/util/hash.cc',
    'leveldb/util/histogram.cc',
    'leveldb/util/logging.cc',
    'leveldb/util/options.cc',
    'leveldb/util/status.cc',
]
sources = plyvel_sources + leveldb_sources

ext_modules = [
    Extension(
        'plyvel._plyvel',
        sources=sources,
        # libraries=['leveldb'],
        extra_compile_args=[
            '-Wall',
            '-g',
            '-I./leveldb',
            '-I./leveldb/include',
            '-DLEVELDB_PLATFORM_POSIX',
        ],
    )
]

setup(
    name='plyvel',
    description="Plyvel, a fast and feature-rich Python interface to LevelDB",
    long_description=get_file_contents('README.rst'),
    url="https://github.com/wbolster/plyvel",
    version=__version__,  # noqa: F821
    author="Wouter Bolsterlee",
    author_email="wouter@bolsterl.ee",
    ext_modules=ext_modules,
    packages=['plyvel'],
    license="BSD License",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Programming Language :: C++",
        "Programming Language :: Cython",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Database",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
