# encoding: UTF-8

from __future__ import unicode_literals

from contextlib import contextmanager
import os
import shutil
import stat
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

from nose.tools import (
    assert_equal,
    assert_is_none,
    assert_is_not_none,
    assert_list_equal,
    assert_raises,
    nottest)

import leveldb
from leveldb import DB

TEST_DB_DIR = 'testdb/'


#
# Utilities
#

def tmp_dir(name):
    return tempfile.mkdtemp(prefix=name + '-', dir=TEST_DB_DIR)


@contextmanager
def tmp_db(name, create=True):
    dir_name = tmp_dir(name)
    if create:
        db = DB(dir_name)
        yield db
        del db
    else:
        yield dir_name
    shutil.rmtree(dir_name)


#
# Test setup and teardown
#

def setup():
    try:
        os.mkdir(TEST_DB_DIR)
    except OSError as exc:
        if exc.errno == 17:
            # Directory already exists; ignore
            pass
        else:
            raise


def teardown():
    try:
        os.rmdir(TEST_DB_DIR)
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
    v = leveldb.__leveldb_version__
    assert v.startswith('1.')


def test_open():
    with tmp_db('read_only_dir', create=False) as name:
        # Opening a DB in a read-only dir should not work
        os.chmod(name, stat.S_IRUSR | stat.S_IXUSR)
        with assert_raises(leveldb.IOError):
            DB(name)

    with tmp_db('úñîçøđê_name') as db:
        pass

    with tmp_db('no_create', create=False) as name:
        with assert_raises(leveldb.Error):
            DB(name, create_if_missing=False)

    with tmp_db('exists', create=False) as name:
        db = DB(name)
        del db
        with assert_raises(leveldb.Error):
            DB(name, error_if_exists=True)

    with assert_raises(TypeError):
        DB(123)

    with assert_raises(ValueError):
        DB('invalid_compression', compression='foobar')

    with tmp_db('many_options', create=False) as name:
        DB(name, create_if_missing=True, error_if_exists=False,
           paranoid_checks=True, write_buffer_size=16 * 1024 * 1024,
           max_open_files=512, lru_cache_size=64 * 1024 * 1024,
           block_size=2 * 1024, block_restart_interval=32,
           compression='snappy', bloom_filter_bits=10)


def test_put():
    with tmp_db('put') as db:
        db.put(b'foo', b'bar')
        db.put(b'foo', b'bar', sync=False)
        db.put(b'foo', b'bar', sync=True)

        for i in xrange(1000):
            key = b'key-%d' % i
            value = b'value-%d' % i
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
        assert_equal(value, db.get(key, fill_cache=False, verify_checksums=None))

        assert_is_none(db.get(b'key-that-does-not-exist'))
        assert_raises(TypeError, db.get, 1)
        assert_raises(TypeError, db.get, 'foo')
        assert_raises(TypeError, db.get, None)
        assert_raises(TypeError, db.get, b'foo', True)


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


def test_batch():
    with tmp_db('batch') as db:
        # Prepare a batch with some data
        batch = db.batch()
        for i in xrange(1000):
            batch.put(b'batch-key-%d' % i, b'value')

        # Delete a key that was also set in the same (pending) batch
        batch.delete(b'batch-key-2')

        # The DB should not have any data before the batch is written
        assert_is_none(db.get(b'batch-key-1'))

        # ...but it should have data afterwards
        batch.write()
        assert_is_not_none(db.get(b'batch-key-1'))
        assert_is_none(db.get(b'batch-key-2'))

        # Batches can be cleared
        batch = db.batch()
        batch.put(b'this-is-never-saved', b'')
        batch.clear()
        batch.write()
        assert_is_none(db.get(b'this-is-never-saved'))

        # Batches take write options
        batch = db.batch(sync=True)
        batch.put(b'batch-key-sync', b'')
        batch.write()


def test_batch_context_manager():
    with tmp_db('batch_context_manager') as db:
        key = b'batch-key'
        assert_is_none(db.get(key))
        with db.batch() as b:
            b.put(key, b'')
        assert_is_not_none(db.get(key))

        # Data should also be written when an exception is raised
        key = b'batch-key-exception'
        assert_is_none(db.get(key))
        with assert_raises(ValueError):
            with db.batch() as b:
                b.put(key, b'')
                raise ValueError()
        assert_is_not_none(db.get(key))


def test_iteration():
    with tmp_db('iteration') as db:
        entries = []
        for i in xrange(100):
            entry = (b'%03d' % i, b'%03d' % i)
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
def test_manual_iteration(db, iter_kwargs, expected_values):
    it = db.iterator(**iter_kwargs)
    first, second, third = expected_values

    assert_equal(first, next(it))
    assert_equal(second, next(it))
    assert_equal(third, next(it))
    with assert_raises(StopIteration):
        next(it)
    with assert_raises(StopIteration):
        # second time may not cause a segfault
        next(it)


@nottest
def test_iterator_single_step(db, iter_kwargs, expected_values):
    it = db.iterator(**iter_kwargs)
    first, second, third = expected_values

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


@nottest
def test_iterator_extremes(db, iter_kwargs, expected_values):
    it = db.iterator(**iter_kwargs)
    first, second, third = expected_values

    # End of iterator
    it.move_to_stop()
    with assert_raises(StopIteration):
        next(it)
    assert_equal(third, it.prev())

    # Begin of iterator
    it.move_to_start()
    with assert_raises(StopIteration):
        it.prev()
    assert_equal(first, next(it))


def test_forward_iteration():
    with tmp_db('forward_iteration') as db:
        db.put(b'1', b'1')
        db.put(b'2', b'2')
        db.put(b'3', b'3')

        expected_values = ('1', '2', '3')
        iter_kwargs = dict(include_key=False)
        test_manual_iteration(db, iter_kwargs, expected_values)
        test_iterator_single_step(db, iter_kwargs, expected_values)
        test_iterator_extremes(db, iter_kwargs, expected_values)


def test_reverse_iteration():
    with tmp_db('reverse_iteration') as db:
        db.put(b'1', b'1')
        db.put(b'2', b'2')
        db.put(b'3', b'3')

        expected_values = ('3', '2', '1')
        iter_kwargs = dict(reverse=True, include_key=False)
        test_manual_iteration(db, iter_kwargs, expected_values)
        test_iterator_single_step(db, iter_kwargs, expected_values)
        test_iterator_extremes(db, iter_kwargs, expected_values)


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

        # Only start
        expected_values = (b'3', b'4', b'5')
        iter_kwargs = dict(start=b'3', include_key=False)
        test_manual_iteration(db, iter_kwargs, expected_values)
        test_iterator_single_step(db, iter_kwargs, expected_values)
        test_iterator_extremes(db, iter_kwargs, expected_values)

        # Only stop
        expected_values = (b'1', b'2', b'3')
        iter_kwargs = dict(stop=b'4', include_key=False)
        test_manual_iteration(db, iter_kwargs, expected_values)
        test_iterator_single_step(db, iter_kwargs, expected_values)
        test_iterator_extremes(db, iter_kwargs, expected_values)

        # Both start and stop
        expected_values = (b'2', b'3', b'4')
        iter_kwargs = dict(start=b'2', stop=b'5', include_key=False)
        test_manual_iteration(db, iter_kwargs, expected_values)
        test_iterator_single_step(db, iter_kwargs, expected_values)
        test_iterator_extremes(db, iter_kwargs, expected_values)


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

        # Only start
        expected_values = (b'5', b'4', b'3')
        iter_kwargs = dict(start=b'3', reverse=True, include_value=False)
        test_manual_iteration(db, iter_kwargs, expected_values)
        test_iterator_single_step(db, iter_kwargs, expected_values)
        test_iterator_extremes(db, iter_kwargs, expected_values)

        # Only stop
        expected_values = (b'3', b'2', b'1')
        iter_kwargs = dict(stop=b'4', reverse=True, include_value=False)
        test_manual_iteration(db, iter_kwargs, expected_values)
        test_iterator_single_step(db, iter_kwargs, expected_values)
        test_iterator_extremes(db, iter_kwargs, expected_values)

        # Both start and stop
        expected_values = (b'3', b'2', b'1')
        iter_kwargs = dict(start=b'1', stop=b'4', reverse=True, include_value=False)
        test_manual_iteration(db, iter_kwargs, expected_values)
        test_iterator_single_step(db, iter_kwargs, expected_values)
        test_iterator_extremes(db, iter_kwargs, expected_values)


def test_range_empty_database():
    with tmp_db('range_empty_database') as db:
        it = db.iterator()
        it.move_to_start()  # no-op (don't crash)
        it.move_to_stop()  # no-op (don't crash)

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


def test_snapshot():
    with tmp_db('snapshot') as db:
        db.put(b'a', b'a')
        db.put(b'b', b'b')

        # Snapshot should have existing values, but not changed values
        snapshot = db.snapshot()
        assert_equal(b'a', snapshot.get(b'a'))
        assert_list_equal(
            ['a', 'b'],
            list(snapshot.iterator(include_value=False)))
        assert_is_none(snapshot.get(b'c'))
        db.delete(b'a')
        db.put(b'c', b'c')
        assert_is_none(snapshot.get(b'c'))
        assert_list_equal(
            [b'a', b'b'],
            list(snapshot.iterator(include_value=False)))

        # New snapshot should reflect latest state
        snapshot = db.snapshot()
        assert_equal(b'c', snapshot.get(b'c'))
        assert_list_equal(
            [b'b', b'c'],
            list(snapshot.iterator(include_value=False)))


def test_compaction():
    # This merely tests that the Python API works correctly, not that
    # LevelDB actually compacts the range
    with tmp_db('compaction') as db:
        db.compact_range()
        db.compact_range(b'a', b'b')
        db.compact_range(start=b'a', stop=b'b')
        db.compact_range(start=b'a', stop=None)
        db.compact_range(start=None, stop=b'b')
        db.compact_range(start=None, stop=None)


def test_repair_db():
    dir_name = tmp_dir('repair')
    db = DB(dir_name)
    db.put(b'foo', b'bar')
    del db
    leveldb.repair_db(dir_name)
    db = DB(dir_name)
    assert_equal(b'bar', db.get(b'foo'))
    del db
    shutil.rmtree(dir_name)


def test_destroy_db():
    dir_name = tmp_dir('destroy')
    db = DB(dir_name)
    db.put(b'foo', b'bar')
    del db
    leveldb.destroy_db(dir_name)
    assert not os.path.lexists(dir_name)
