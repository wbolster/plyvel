# encoding: UTF-8

from __future__ import unicode_literals

from contextlib import contextmanager
import os
import shutil
import stat
import sys
import tempfile

try:
    from itertools import izip
except ImportError:
    # Python 3
    izip = zip

try:
    xrange
except NameError:
    # Python 3
    xrange = range

from nose.plugins.skip import SkipTest
from nose.tools import (
    assert_equal,
    assert_greater_equal,
    assert_is_instance,
    assert_is_none,
    assert_is_not_none,
    assert_list_equal,
    assert_raises,
    assert_sequence_equal,
    nottest)

import plyvel
from plyvel import DB

TEST_DBS_DIR = 'testdb/'


#
# Utilities
#

@contextmanager
def tmp_db(name_prefix, create=True, delete=True, **kwargs):
    name = tempfile.mkdtemp(prefix=name_prefix + '-', dir=TEST_DBS_DIR)
    if create:
        db = DB(name, create_if_missing=True, error_if_exists=True, **kwargs)
        yield db
        db.close()
    else:
        yield name

    if delete:
        shutil.rmtree(name)


#
# Test setup and teardown
#

def setup():
    try:
        os.mkdir(TEST_DBS_DIR)
    except OSError as exc:
        if exc.errno == 17:
            # Directory already exists; ignore
            pass
        else:
            raise


def teardown():
    try:
        os.rmdir(TEST_DBS_DIR)
    except OSError as exc:
        if exc.errno == 39:
            # Directory not empty; some tests failed
            pass
        else:
            raise


#
# Actual tests
#

def test_version():
    v = plyvel.__leveldb_version__
    assert v.startswith('1.')


def test_open():
    with tmp_db('read_only_dir', create=False) as name:
        # Opening a DB in a read-only dir should not work
        os.chmod(name, stat.S_IRUSR | stat.S_IXUSR)
        with assert_raises(plyvel.IOError):
            DB(name)

    with tmp_db('no_create', create=False) as name:
        with assert_raises(plyvel.Error):
            DB(name, create_if_missing=False)

    with tmp_db('exists', create=False) as name:
        db = DB(name, create_if_missing=True)
        db.close()
        with assert_raises(plyvel.Error):
            DB(name, error_if_exists=True)

    with assert_raises(TypeError):
        DB(123)

    with assert_raises(TypeError):
        DB('invalid_option_types', write_buffer_size='invalid')

    with assert_raises(TypeError):
        DB('invalid_option_types', lru_cache_size='invalid')

    with assert_raises(ValueError):
        DB('invalid_compression', compression='invalid',
           create_if_missing=True)

    with tmp_db('no_compression', create=False) as name:
        DB(name, compression=None, create_if_missing=True)

    with tmp_db('many_options', create=False) as name:
        DB(name, create_if_missing=True, error_if_exists=False,
           paranoid_checks=True, write_buffer_size=16 * 1024 * 1024,
           max_open_files=512, lru_cache_size=64 * 1024 * 1024,
           block_size=2 * 1024, block_restart_interval=32,
           compression='snappy', bloom_filter_bits=10)


def test_open_unicode_name():
    if sys.getfilesystemencoding().lower() != 'utf-8':
        # XXX: letter casing differs between Python 2 and 3
        raise SkipTest("Not running with UTF-8 file system encoding")

    with tmp_db('úñîçøđê_name'):
        pass


def test_open_close():
    with tmp_db('open_close', create=False) as name:
        # Create a database with options that result in additional
        # object allocation (e.g. LRU cache).
        db = DB(name,
                create_if_missing=True,
                lru_cache_size=1024 * 1024,
                bloom_filter_bits=10)
        db.put(b'key', b'value')
        wb = db.write_batch()
        sn = db.snapshot()
        it = db.iterator()
        snapshot_it = sn.iterator()

        # Close the database
        db.close()
        assert db.closed

        # Expect runtime errors for operations on the database,
        with assert_raises(RuntimeError):
            db.get(b'key')
        with assert_raises(RuntimeError):
            db.put(b'key', b'value')
        with assert_raises(RuntimeError):
            db.delete(b'key')

        # ... on write batches,
        with assert_raises(RuntimeError):
            wb.put(b'key', b'value')

        # ... on snapshots,
        assert_raises(RuntimeError, db.snapshot)
        with assert_raises(RuntimeError):
            sn.get(b'key')

        # ... on iterators,
        with assert_raises(RuntimeError):
            next(it)

        # ... and on snapshot iterators,
        with assert_raises(RuntimeError):
            next(snapshot_it)


def test_large_lru_cache():
    # Use a 2 GB size (does not fit in a 32-bit signed int)
    with tmp_db('large_lru_cache', lru_cache_size=2 * 1024**3):
        pass


def test_put():
    with tmp_db('put') as db:
        db.put(b'foo', b'bar')
        db.put(b'foo', b'bar', sync=False)
        db.put(b'foo', b'bar', sync=True)

        for i in xrange(1000):
            key = ('key-%d' % i).encode('ascii')
            value = ('value-%d' % i).encode('ascii')
            db.put(key, value)

        assert_raises(TypeError, db.put, b'foo', 12)
        assert_raises(TypeError, db.put, 12, 'foo')


def test_get():
    with tmp_db('get') as db:
        key = b'the-key'
        value = b'the-value'
        assert_is_none(db.get(key))
        db.put(key, value)
        assert_equal(value, db.get(key))
        assert_equal(value, db.get(key, verify_checksums=True))
        assert_equal(value, db.get(key, verify_checksums=False))
        assert_equal(value, db.get(key, verify_checksums=None))
        assert_equal(value, db.get(key, fill_cache=True))
        assert_equal(value, db.get(key, fill_cache=False,
                                   verify_checksums=None))

        key2 = b'key-that-does-not-exist'
        value2 = b'default-value'
        assert_is_none(db.get(key2))
        assert_equal(value2, db.get(key2, value2))
        assert_equal(value2, db.get(key2, default=value2))

        assert_raises(TypeError, db.get, 1)
        assert_raises(TypeError, db.get, 'key')
        assert_raises(TypeError, db.get, None)
        assert_raises(TypeError, db.get, b'foo', b'default', True)


def test_delete():
    with tmp_db('delete') as db:
        # Put and delete a key
        key = b'key-that-will-be-deleted'
        db.put(key, b'')
        assert_is_not_none(db.get(key))
        db.delete(key)
        assert_is_none(db.get(key))

        # The .delete() method also takes write options
        db.put(key, b'')
        db.delete(key, sync=True)


def test_null_bytes():
    with tmp_db('null_bytes') as db:
        key = b'key\x00\x01'
        value = b'\x00\x00\x01'
        db.put(key, value)
        assert_equal(value, db.get(key))
        db.delete(key)
        assert_is_none(db.get(key))


def test_write_batch():
    with tmp_db('write_batch') as db:
        # Prepare a batch with some data
        batch = db.write_batch()
        for i in xrange(1000):
            batch.put(('batch-key-%d' % i).encode('ascii'), b'value')

        # Delete a key that was also set in the same (pending) batch
        batch.delete(b'batch-key-2')

        # The DB should not have any data before the batch is written
        assert_is_none(db.get(b'batch-key-1'))

        # ...but it should have data afterwards
        batch.write()
        assert_is_not_none(db.get(b'batch-key-1'))
        assert_is_none(db.get(b'batch-key-2'))

        # Batches can be cleared
        batch = db.write_batch()
        batch.put(b'this-is-never-saved', b'')
        batch.clear()
        batch.write()
        assert_is_none(db.get(b'this-is-never-saved'))

        # Batches take write options
        batch = db.write_batch(sync=True)
        batch.put(b'batch-key-sync', b'')
        batch.write()


def test_write_batch_context_manager():
    with tmp_db('write_batch_context_manager') as db:
        key = b'batch-key'
        assert_is_none(db.get(key))
        with db.write_batch() as wb:
            wb.put(key, b'')
        assert_is_not_none(db.get(key))

        # Data should also be written when an exception is raised
        key = b'batch-key-exception'
        assert_is_none(db.get(key))
        with assert_raises(ValueError):
            with db.write_batch() as wb:
                wb.put(key, b'')
                raise ValueError()
        assert_is_not_none(db.get(key))


def test_write_batch_transaction():
    with tmp_db('write_batch_transaction') as db:
        with assert_raises(ValueError):
            with db.write_batch(transaction=True) as wb:
                wb.put(b'key', b'value')
                raise ValueError()

        assert_list_equal([], list(db.iterator()))


def test_iteration():
    with tmp_db('iteration') as db:
        entries = []
        for i in xrange(100):
            entry = (
                ('%03d' % i).encode('ascii'),
                ('%03d' % i).encode('ascii'))
            entries.append(entry)

        for k, v in entries:
            db.put(k, v)

        for entry, expected in izip(entries, db):
            assert_equal(entry, expected)


def test_iterator_return():
    with tmp_db('iteration') as db:
        db.put(b'key', b'value')

        for key, value in db:
            assert_equal(key, b'key')
            assert_equal(value, b'value')

        for key, value in db.iterator():
            assert_equal(key, b'key')
            assert_equal(value, b'value')

        for key in db.iterator(include_value=False):
            assert_equal(key, b'key')

        for value in db.iterator(include_key=False):
            assert_equal(value, b'value')

        for ret in db.iterator(include_key=False, include_value=False):
            assert_is_none(ret)


@nottest
def test_iterator_behaviour(db, iter_kwargs, expected_values):
    first, second, third = expected_values
    is_forward = not iter_kwargs.get('reverse', False)

    # Simple iteration
    it = db.iterator(**iter_kwargs)
    assert_equal(first, next(it))
    assert_equal(second, next(it))
    assert_equal(third, next(it))
    with assert_raises(StopIteration):
        next(it)
    with assert_raises(StopIteration):
        # second time may not cause a segfault
        next(it)

    # Single steps, both next() and .prev()
    it = db.iterator(**iter_kwargs)
    assert_equal(first, next(it))
    assert_equal(first, it.prev())
    assert_equal(first, next(it))
    assert_equal(first, it.prev())
    with assert_raises(StopIteration):
        it.prev()
    assert_equal(first, next(it))
    assert_equal(second, next(it))
    assert_equal(third, next(it))
    with assert_raises(StopIteration):
        next(it)
    assert_equal(third, it.prev())
    assert_equal(second, it.prev())

    # End of iterator
    it = db.iterator(**iter_kwargs)
    if is_forward:
        it.seek_to_stop()
    else:
        it.seek_to_start()
    with assert_raises(StopIteration):
        next(it)
    assert_equal(third, it.prev())

    # Begin of iterator
    it = db.iterator(**iter_kwargs)
    if is_forward:
        it.seek_to_start()
    else:
        it.seek_to_stop()
    with assert_raises(StopIteration):
        it.prev()
    assert_equal(first, next(it))


def test_forward_iteration():
    with tmp_db('forward_iteration') as db:
        db.put(b'1', b'1')
        db.put(b'2', b'2')
        db.put(b'3', b'3')

        test_iterator_behaviour(
            db,
            iter_kwargs=dict(include_key=False),
            expected_values=(b'1', b'2', b'3'))


def test_reverse_iteration():
    with tmp_db('reverse_iteration') as db:
        db.put(b'1', b'1')
        db.put(b'2', b'2')
        db.put(b'3', b'3')

        test_iterator_behaviour(
            db,
            iter_kwargs=dict(reverse=True, include_key=False),
            expected_values=(b'3', b'2', b'1'))


def test_range_iteration():
    with tmp_db('range_iteration') as db:
        db.put(b'1', b'1')
        db.put(b'2', b'2')
        db.put(b'3', b'3')
        db.put(b'4', b'4')
        db.put(b'5', b'5')

        assert_list_equal(
            [b'2', b'3', b'4', b'5'],
            list(db.iterator(start=b'2', include_value=False)))

        assert_list_equal(
            [b'1', b'2'],
            list(db.iterator(stop=b'3', include_value=False)))

        assert_list_equal(
            [b'1', b'2'],
            list(db.iterator(start=b'0', stop=b'3', include_value=False)))

        assert_list_equal(
            [],
            list(db.iterator(start=b'3', stop=b'0')))

        # Only start (inclusive)
        test_iterator_behaviour(
            db,
            iter_kwargs=dict(start=b'3', include_key=False),
            expected_values=(b'3', b'4', b'5'))

        # Only start (exclusive)
        test_iterator_behaviour(
            db,
            iter_kwargs=dict(start=b'2', include_key=False,
                             include_start=False),
            expected_values=(b'3', b'4', b'5'))

        # Only stop (exclusive)
        test_iterator_behaviour(
            db,
            iter_kwargs=dict(stop=b'4', include_key=False),
            expected_values=(b'1', b'2', b'3'))

        # Only stop (inclusive)
        test_iterator_behaviour(
            db,
            iter_kwargs=dict(stop=b'3', include_key=False, include_stop=True),
            expected_values=(b'1', b'2', b'3'))

        # Both start and stop
        test_iterator_behaviour(
            db,
            iter_kwargs=dict(start=b'2', stop=b'5', include_key=False),
            expected_values=(b'2', b'3', b'4'))


def test_reverse_range_iteration():
    with tmp_db('reverse_range_iteration') as db:
        db.put(b'1', b'1')
        db.put(b'2', b'2')
        db.put(b'3', b'3')
        db.put(b'4', b'4')
        db.put(b'5', b'5')

        assert_list_equal(
            [],
            list(db.iterator(start=b'3', stop=b'0', reverse=True)))

        # Only start (inclusive)
        test_iterator_behaviour(
            db,
            iter_kwargs=dict(start=b'3', reverse=True, include_value=False),
            expected_values=(b'5', b'4', b'3'))

        # Only start (exclusive)
        test_iterator_behaviour(
            db,
            iter_kwargs=dict(start=b'2', reverse=True, include_value=False,
                             include_start=False),
            expected_values=(b'5', b'4', b'3'))

        # Only stop (exclusive)
        test_iterator_behaviour(
            db,
            iter_kwargs=dict(stop=b'4', reverse=True, include_value=False),
            expected_values=(b'3', b'2', b'1'))

        # Only stop (inclusive)
        test_iterator_behaviour(
            db,
            iter_kwargs=dict(stop=b'3', reverse=True, include_value=False,
                             include_stop=True),
            expected_values=(b'3', b'2', b'1'))

        # Both start and stop
        test_iterator_behaviour(
            db,
            iter_kwargs=dict(start=b'1', stop=b'4', reverse=True,
                             include_value=False),
            expected_values=(b'3', b'2', b'1'))


def test_out_of_range_iterations():
    with tmp_db('out_of_range_iterations') as db:
        db.put(b'1', b'1')
        db.put(b'3', b'3')
        db.put(b'4', b'4')
        db.put(b'5', b'5')
        db.put(b'7', b'7')

        def t(expected, **kwargs):
            kwargs['include_value'] = False
            assert_equal(expected, b''.join((db.iterator(**kwargs))))

        # Out of range start key
        t(b'3457', start=b'2')
        t(b'3457', start=b'2', include_start=False)

        # Out of range stop key
        t(b'5431', stop=b'6', reverse=True)
        t(b'5431', stop=b'6', include_stop=True, reverse=True)

        # Out of range prefix
        t(b'', prefix=b'0', include_start=True)
        t(b'', prefix=b'0', include_start=False)
        t(b'', prefix=b'8', include_stop=True, reverse=True)
        t(b'', prefix=b'8', include_stop=False, reverse=True)


def test_range_empty_database():
    with tmp_db('range_empty_database') as db:
        it = db.iterator()
        it.seek_to_start()  # no-op (don't crash)
        it.seek_to_stop()  # no-op (don't crash)

        it = db.iterator()
        with assert_raises(StopIteration):
            next(it)

        it = db.iterator()
        with assert_raises(StopIteration):
            it.prev()
        with assert_raises(StopIteration):
            next(it)


def test_iterator_single_entry():
    with tmp_db('iterator_single_entry') as db:
        key = b'key'
        value = b'value'
        db.put(key, value)

        it = db.iterator(include_value=False)
        assert_equal(key, next(it))
        assert_equal(key, it.prev())
        assert_equal(key, next(it))
        assert_equal(key, it.prev())
        with assert_raises(StopIteration):
            it.prev()
        assert_equal(key, next(it))
        with assert_raises(StopIteration):
            next(it)


def test_iterator_seeking():
    with tmp_db('iterator_seeking') as db:
        db.put(b'1', b'1')
        db.put(b'2', b'2')
        db.put(b'3', b'3')
        db.put(b'4', b'4')
        db.put(b'5', b'5')

        it = db.iterator(include_value=False)
        it.seek_to_start()
        with assert_raises(StopIteration):
            it.prev()
        assert_equal(b'1', next(it))
        it.seek_to_start()
        assert_equal(b'1', next(it))
        it.seek_to_stop()
        with assert_raises(StopIteration):
            next(it)
        assert_equal(b'5', it.prev())

        # Seek to a specific key
        it.seek(b'2')
        assert_equal(b'2', next(it))
        assert_equal(b'3', next(it))
        assert_list_equal([b'4', b'5'], list(it))
        it.seek(b'2')
        assert_equal(b'1', it.prev())

        # Seek to keys that sort between/before/after existing keys
        it.seek(b'123')
        assert_equal(b'2', next(it))
        it.seek(b'6')
        with assert_raises(StopIteration):
            next(it)
        it.seek(b'0')
        with assert_raises(StopIteration):
            it.prev()
        assert_equal(b'1', next(it))
        it.seek(b'4')
        it.seek(b'3')
        assert_equal(b'3', next(it))

        # Seek in a reverse iterator
        it = db.iterator(include_value=False, reverse=True)
        it.seek(b'6')
        assert_equal(b'5', next(it))
        assert_equal(b'4', next(it))
        it.seek(b'1')
        with assert_raises(StopIteration):
            next(it)
        assert_equal(b'1', it.prev())

        # Seek in iterator with start key
        it = db.iterator(start=b'2', include_value=False)
        assert_equal(b'2', next(it))
        it.seek(b'2')
        assert_equal(b'2', next(it))
        it.seek(b'0')
        assert_equal(b'2', next(it))
        it.seek_to_start()
        assert_equal(b'2', next(it))

        # Seek in iterator with stop key
        it = db.iterator(stop=b'3', include_value=False)
        assert_equal(b'1', next(it))
        it.seek(b'2')
        assert_equal(b'2', next(it))
        it.seek(b'5')
        with assert_raises(StopIteration):
            next(it)
        it.seek(b'5')
        assert_equal(b'2', it.prev())
        it.seek_to_stop()
        with assert_raises(StopIteration):
            next(it)
        it.seek_to_stop()
        assert_equal(b'2', it.prev())

        # Seek in iterator with both start and stop keys
        it = db.iterator(start=b'2', stop=b'5', include_value=False)
        it.seek(b'0')
        assert_equal(b'2', next(it))
        it.seek(b'5')
        with assert_raises(StopIteration):
            next(it)
        it.seek(b'5')
        assert_equal(b'4', it.prev())

        # Seek in reverse iterator with start and stop key
        it = db.iterator(
            reverse=True, start=b'2', stop=b'4', include_value=False)
        it.seek(b'5')
        assert_equal(b'3', next(it))
        it.seek(b'1')
        assert_equal(b'2', it.prev())
        it.seek_to_start()
        with assert_raises(StopIteration):
            next(it)
        it.seek_to_stop()
        assert_equal(b'3', next(it))


def test_iterator_boundaries():
    with tmp_db('iterator_boundaries') as db:
        db.put(b'1', b'1')
        db.put(b'2', b'2')
        db.put(b'3', b'3')
        db.put(b'4', b'4')
        db.put(b'5', b'5')

        def t(expected, **kwargs):
            kwargs.update(include_value=False)
            actual = b''.join(db.iterator(**kwargs))
            assert_equal(expected, actual)

        t(b'12345')
        t(b'345', start=b'2', include_start=False)
        t(b'1234', stop=b'5', include_start=False)
        t(b'12345', stop=b'5', include_stop=True)
        t(b'2345', start=b'2', stop=b'5', include_stop=True)
        t(b'2345', start=b'2', stop=b'5', include_stop=True)
        t(b'345', start=b'3', include_stop=False)
        t(b'45', start=b'3', include_start=False, include_stop=False)


def test_iterator_prefix():
    with tmp_db('iterator_prefix') as db:
        keys = [
            b'a1', b'a2', b'a3', b'aa4', b'aa5',
            b'b1', b'b2', b'b3', b'b4', b'b5',
            b'c1', b'c\xff', b'c\x00',
            b'\xff\xff', b'\xff\xffa', b'\xff\xff\xff',
        ]
        for key in keys:
            db.put(key, b'')

        assert_raises(TypeError, db.iterator, prefix=b'abc', start=b'a')
        assert_raises(TypeError, db.iterator, prefix=b'abc', stop=b'a')

        def t(*args, **kwargs):
            # Positional arguments are the expected ones, keyword
            # arguments are passed to db.iterator()
            kwargs.update(include_value=False)
            actual = list(db.iterator(**kwargs))
            assert_sequence_equal(args, actual)

        t(*sorted(keys), prefix=b'')
        t(prefix=b'd')
        t(b'b1', prefix=b'b1')
        t(b'a1', b'a2', b'a3', b'aa4', b'aa5', prefix=b'a')
        t(b'aa4', b'aa5', prefix=b'aa')
        t(b'\xff\xff', b'\xff\xffa', b'\xff\xff\xff', prefix=b'\xff\xff')

        # The include_start and include_stop make no sense, so should
        # not affect the behaviour
        t(b'a1', b'a2', b'a3', b'aa4', b'aa5',
          prefix=b'a', include_start=False, include_stop=True)


def test_snapshot():
    with tmp_db('snapshot') as db:
        db.put(b'a', b'a')
        db.put(b'b', b'b')

        # Snapshot should have existing values, but not changed values
        snapshot = db.snapshot()
        assert_equal(b'a', snapshot.get(b'a'))
        assert_list_equal(
            [b'a', b'b'],
            list(snapshot.iterator(include_value=False)))
        assert_is_none(snapshot.get(b'c'))
        db.delete(b'a')
        db.put(b'c', b'c')
        assert_is_none(snapshot.get(b'c'))
        assert_equal(b'd', snapshot.get(b'c', b'd'))
        assert_equal(b'd', snapshot.get(b'c', default=b'd'))
        assert_list_equal(
            [b'a', b'b'],
            list(snapshot.iterator(include_value=False)))

        # New snapshot should reflect latest state
        snapshot = db.snapshot()
        assert_equal(b'c', snapshot.get(b'c'))
        assert_list_equal(
            [b'b', b'c'],
            list(snapshot.iterator(include_value=False)))

        # Snapshots are directly iterable, just like DB
        assert_list_equal(
            [b'b', b'c'],
            list(k for k, v in snapshot))


def test_property():
    with tmp_db('property') as db:
        with assert_raises(TypeError):
            db.get_property()

        with assert_raises(TypeError):
            db.get_property(42)

        assert_is_none(db.get_property(b'does-not-exist'))

        properties = [
            b'leveldb.stats',
            b'leveldb.sstables',
            b'leveldb.num-files-at-level0',
        ]
        for prop in properties:
            assert_is_instance(db.get_property(prop), bytes)


def test_compaction():
    with tmp_db('compaction') as db:
        db.compact_range()
        db.compact_range(start=b'a', stop=b'b')
        db.compact_range(start=b'a')
        db.compact_range(stop=b'b')


def test_approximate_sizes():
    with tmp_db('approximate_sizes', create=False) as name:

        # Write some data to a fresh database
        db = DB(name, create_if_missing=True, error_if_exists=True)
        value = b'a' * 100
        with db.write_batch() as wb:
            for i in xrange(1000):
                key = bytes(i) * 100
                wb.put(key, value)

        # Close and reopen the database
        db.close()
        del wb, db
        db = DB(name, create_if_missing=False)

        with assert_raises(TypeError):
            db.approximate_size(1, 2)

        with assert_raises(TypeError):
            db.approximate_sizes(None)

        with assert_raises(TypeError):
            db.approximate_sizes((1, 2))

        # Test single range
        assert_greater_equal(db.approximate_size(b'1', b'2'), 0)

        # Test multiple ranges
        assert_list_equal([], db.approximate_sizes())
        assert_greater_equal(db.approximate_sizes((b'1', b'2'))[0], 0)

        ranges = [
            (b'1', b'3'),
            (b'', b'\xff'),
        ]
        assert_equal(len(ranges), len(db.approximate_sizes(*ranges)))


def test_repair_db():
    with tmp_db('repair', create=False) as name:
        db = DB(name, create_if_missing=True)
        db.put(b'foo', b'bar')
        db.close()
        del db

        plyvel.repair_db(name)
        db = DB(name)
        assert_equal(b'bar', db.get(b'foo'))


def test_destroy_db():
    with tmp_db('destroy', create=False, delete=False) as name:
        db = DB(name, create_if_missing=True)
        db.put(b'foo', b'bar')
        db.close()
        del db

        plyvel.destroy_db(name)
        assert not os.path.lexists(name)


def test_threading():
    from threading import Thread, current_thread
    import time
    import itertools
    from random import randint

    with tmp_db('threading') as db:

        N_THREADS_PER_FUNC = 5

        def bulk_insert(db):
            name = current_thread().name
            v = name.encode('ascii') * randint(300, 700)
            for n in xrange(randint(1000, 8000)):
                rev = '{:x}'.format(n)[::-1]
                k = '{}: {}'.format(rev, name).encode('ascii')
                db.put(k, v)

        def iterate_full(db):
            for i in xrange(randint(4, 7)):
                for key, value in db.iterator(reverse=True):
                    pass

        def iterate_short(db):
            for i in xrange(randint(200, 700)):
                it = db.iterator()
                list(itertools.islice(it, randint(50, 100)))

        def close_db(db):
            time.sleep(1)
            db.close()

        funcs = [
            bulk_insert,
            iterate_full,
            iterate_short,

            # XXX: This this will usually cause a segfault since
            # unexpectedly closing a database may crash threads using
            # iterators:
            # close_db,
        ]

        threads = []
        for func in funcs:
            for n in xrange(N_THREADS_PER_FUNC):
                t = Thread(target=func, args=(db,))
                t.start()
                threads.append(t)

        for t in threads:
            t.join()


def test_invalid_comparator():
    with tmp_db('invalid_comparator', create=False) as name:

        with assert_raises(ValueError):
            DB(name, comparator=None, comparator_name=b'invalid')

        with assert_raises(TypeError):
            DB(name,
               comparator=lambda x, y: 1,
               comparator_name=12)

        with assert_raises(TypeError):
            DB(name,
               comparator=b'not-a-callable',
               comparator_name=b'invalid')


def test_comparator():
    def comparator(a, b):
        a = a.lower()
        b = b.lower()
        if a < b:
            return -1
        if a > b:
            return 1
        else:
            return 0

    comparator_name = b"CaseInsensitiveComparator"

    with tmp_db('comparator', create=False) as name:
        db = DB(name,
                create_if_missing=True,
                comparator=comparator,
                comparator_name=comparator_name)

        keys = [
            b'aaa',
            b'BBB',
            b'ccc',
        ]

        with db.write_batch() as wb:
            for key in keys:
                wb.put(key, b'')

        assert_list_equal(
            sorted(keys, key=lambda s: s.lower()),
            list(db.iterator(include_value=False)))


def test_prefixed_db():
    with tmp_db('prefixed') as db:
        for prefix in (b'a', b'b'):
            for i in xrange(1000):
                key = prefix + '{:03d}'.format(i).encode('ascii')
                db.put(key, b'')

        db_a = db.prefixed_db(b'a')
        db_b = db.prefixed_db(b'b')

        # Access original db
        assert db_a.db is db

        # Basic operations
        key = b'123'
        assert_is_not_none(db_a.get(key))
        db_a.put(key, b'foo')
        assert_equal(b'foo', db_a.get(key))
        db_a.delete(key)
        assert_is_none(db_a.get(key))
        assert_equal(b'v', db_a.get(key, b'v'))
        assert_equal(b'v', db_a.get(key, default=b'v'))
        db_a.put(key, b'foo')
        assert_equal(b'foo', db.get(b'a123'))

        # Iterators
        assert_equal(1000, len(list(db_a)))
        it = db_a.iterator(include_value=False)
        assert_equal(b'000', next(it))
        assert_equal(b'001', next(it))
        assert_equal(998, len(list(it)))
        it = db_a.iterator(start=b'900')
        assert_equal(100, len(list(it)))
        it = db_a.iterator(stop=b'012', include_stop=False)
        assert_equal(12, len(list(it)))
        it = db_a.iterator(stop=b'012', include_stop=True)
        assert_equal(13, len(list(it)))
        it = db_a.iterator(include_stop=True)
        assert_equal(1000, len(list(it)))
        it = db_a.iterator(prefix=b'10')
        assert_equal(10, len(list(it)))
        it = db_a.iterator(include_value=False)
        it.seek(b'500')
        assert_equal(500, len(list(it)))
        it.seek_to_start()
        assert_equal(1000, len(list(it)))
        it.seek_to_stop()
        assert_equal(b'999', it.prev())
        it = db_b.iterator()
        it.seek_to_start()
        assert_raises(StopIteration, it.prev)
        it.seek_to_stop()
        with assert_raises(StopIteration):
            next(it)

        # Snapshots
        sn_a = db_a.snapshot()
        assert_equal(b'', sn_a.get(b'042'))
        db_a.put(b'042', b'new')
        assert_equal(b'', sn_a.get(b'042'))
        assert_equal(b'new', db_a.get(b'042'))
        assert_equal(b'x', db_a.get(b'foo', b'x'))
        assert_equal(b'x', db_a.get(b'foo', default=b'x'))

        # Snapshot iterators
        sn_a.iterator()
        it = sn_a.iterator(
            start=b'900', include_start=False, include_value=False)
        assert_equal(b'901', next(it))
        assert_equal(98, len(list(it)))

        # Write batches
        wb = db_a.write_batch()
        wb.put(b'0002', b'foo')
        wb.delete(b'0003')
        wb.write()
        assert_equal(b'foo', db_a.get(b'0002'))
        assert_is_none(db_a.get(b'0003'))

        # Delete all data in db_a
        for key in db_a.iterator(include_value=False):
            db_a.delete(key)
        assert_equal(0, len(list(db_a)))

        # The complete db and the 'b' prefix should remain untouched
        assert_equal(1000, len(list(db)))
        assert_equal(1000, len(list(db_b)))

        # Prefixed prefixed databases (recursive)
        db_b12 = db_b.prefixed_db(b'12')
        it = db_b12.iterator(include_value=False)
        assert_equal(b'0', next(it))
        assert_equal(9, len(list(it)))
