
from contextlib import contextmanager
from itertools import izip
from os import mkdir, rmdir
from shutil import rmtree
from tempfile import mkdtemp

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
    return mkdtemp(prefix=name + '-', dir=TEST_DB_DIR)


@contextmanager
def tmp_db(name):
    dir_name = tmp_dir(name)
    db = DB(dir_name)
    yield db
    del db
    rmtree(dir_name)


#
# Test setup and teardown
#

def setup():
    try:
        mkdir(TEST_DB_DIR)
    except OSError as exc:
        if exc.errno == 17:
            # Directory already exists; ignore
            pass
        else:
            raise


def teardown():
    try:
        rmdir(TEST_DB_DIR)
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
    assert isinstance(v, basestring)
    assert v.startswith('1.')


# TODO: use different directories for open/close tests
# def test_open_close():
#     somedb = DB(TEST_DB_DIR2)
#     print somedb
#     del somedb


def test_put():
    with tmp_db('put') as db:
        db.put('foo', 'bar')
        db.put('foo', 'bar', sync=False)
        db.put('foo', 'bar', sync=True)

        for i in xrange(1000):
            key = 'key-%d' % i
            value = 'value-%d' % i
            db.put(key, value)

        assert_raises(TypeError, db.put, 'foo', 12)
        assert_raises(TypeError, db.put, 12, 'foo')


def test_get():
    with tmp_db('get') as db:
        key = 'the-key'
        value = 'the-value'
        assert_is_none(db.get(key))
        db.put(key, value)
        assert_equal(value, db.get(key))
        assert_equal(value, db.get(key, verify_checksums=True))
        assert_equal(value, db.get(key, verify_checksums=False))
        assert_equal(value, db.get(key, verify_checksums=None))
        assert_equal(value, db.get(key, fill_cache=True))
        assert_equal(value, db.get(key, fill_cache=False, verify_checksums=None))

        assert_is_none(db.get('key-that-does-not-exist'))

        assert_raises(TypeError, db.get, 1)
        assert_raises(TypeError, db.get, u'foo')
        assert_raises(TypeError, db.get, None)

        assert_raises(TypeError, db.get, 'foo', True)


def test_delete():
    with tmp_db('delete') as db:
        # Put and delete a key
        key = 'key-that-will-be-deleted'
        db.put(key, '')
        assert_is_not_none(db.get(key))
        db.delete(key)
        assert_is_none(db.get(key))

        # The .delete() method also takes write options
        db.put(key, '')
        db.delete(key, sync=True)


def test_batch():
    with tmp_db('batch') as db:
        # Prepare a batch with some data
        batch = db.batch()
        for i in xrange(1000):
            batch.put('batch-key-%d' % i, 'value')

        # Delete a key that was also set in the same (pending) batch
        batch.delete('batch-key-2')

        # The DB should not have any data before the batch is written
        assert_is_none(db.get('batch-key-1'))

        # ...but it should have data afterwards
        batch.write()
        assert_is_not_none(db.get('batch-key-1'))
        assert_is_none(db.get('batch-key-2'))

        # Batches can be cleared
        batch = db.batch()
        batch.put('this-is-never-saved', '')
        batch.clear()
        batch.write()
        assert_is_none(db.get('this-is-never-saved'))

        # Batches take write options
        batch = db.batch(sync=True)
        batch.put('batch-key-sync', '')
        batch.write()


def test_batch_context_manager():
    with tmp_db('batch_context_manager') as db:
        key = 'batch-key'
        assert_is_none(db.get(key))
        with db.batch() as b:
            b.put(key, '')
        assert_is_not_none(db.get(key))

        # Data should also be written when an exception is raised
        key = 'batch-key-exception'
        assert_is_none(db.get(key))
        with assert_raises(ValueError):
            with db.batch() as b:
                b.put(key, '')
                raise ValueError()
        assert_is_not_none(db.get(key))


def test_iteration():
    with tmp_db('iteration') as db:
        entries = []
        for i in xrange(100):
            entry = ('%03d' % i, '%03d' % i)
            entries.append(entry)

        for k, v in entries:
            db.put(k, v)

        for entry, expected in izip(entries, db):
            assert_equal(entry, expected)


def test_iterator_return():
    with tmp_db('iteration') as db:
        db.put('key', 'value')

    for key, value in db:
        assert_equal(key, 'key')
        assert_equal(value, 'value')

    for key, value in db.iterator():
        assert_equal(key, 'key')
        assert_equal(value, 'value')

    for key in db.iterator(include_value=False):
        assert_equal(key, 'key')

    for value in db.iterator(include_key=False):
        assert_equal(value, 'value')

    for ret in db.iterator(include_key=False, include_value=False):
        assert_is_none(ret)


@nottest
def test_manual_iteration(db, iter_kwargs, expected_values):
    it = db.iterator(**iter_kwargs)
    first, second, third = expected_values

    assert_equal(first, next(it))
    assert_equal(second, next(it))
    assert_equal(third, it.next())
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
    assert_equal(first, it.next())
    assert_equal(second, it.next())
    assert_equal(third, it.next())
    with assert_raises(StopIteration):
        it.next()
    assert_equal(third, it.prev())
    assert_equal(second, it.prev())


@nottest
def test_iterator_extremes(db, iter_kwargs, expected_values):
    it = db.iterator(**iter_kwargs)
    first, second, third = expected_values

    # End of iterator
    it.move_to_stop()
    with assert_raises(StopIteration):
        it.next()
    assert_equal(third, it.prev())

    # Begin of iterator
    it.move_to_start()
    with assert_raises(StopIteration):
        it.prev()
    assert_equal(first, next(it))


def test_forward_iteration():
    with tmp_db('forward_iteration') as db:
        db.put('1', '1')
        db.put('2', '2')
        db.put('3', '3')

        expected_values = ('1', '2', '3')
        iter_kwargs = dict(include_key=False)
        test_manual_iteration(db, iter_kwargs, expected_values)
        test_iterator_single_step(db, iter_kwargs, expected_values)
        test_iterator_extremes(db, iter_kwargs, expected_values)


def test_backward_iteration():
    with tmp_db('backward_iteration') as db:
        db.put('1', '1')
        db.put('2', '2')
        db.put('3', '3')

        expected_values = ('3', '2', '1')
        iter_kwargs = dict(reverse=True, include_key=False)
        test_manual_iteration(db, iter_kwargs, expected_values)
        test_iterator_single_step(db, iter_kwargs, expected_values)
        test_iterator_extremes(db, iter_kwargs, expected_values)


def test_range_iteration():
    with tmp_db('range_iteration') as db:
        db.put('1', '1')
        db.put('2', '2')
        db.put('3', '3')
        db.put('4', '4')
        db.put('5', '5')

        assert_list_equal(
            ['2', '3', '4', '5'],
            list(db.iterator(start='2', include_value=False)))

        assert_list_equal(
            ['1', '2'],
            list(db.iterator(stop='3', include_value=False)))

        assert_list_equal(
            ['1', '2'],
            list(db.iterator(start='0', stop='3', include_value=False)))

        assert_list_equal([], list(db.iterator(start='3', stop='0')))

        expected_values = ('2', '3', '4')
        iter_kwargs = dict(start='2', stop='5', include_key=False)
        test_manual_iteration(db, iter_kwargs, expected_values)
        test_iterator_single_step(db, iter_kwargs, expected_values)
        test_iterator_extremes(db, iter_kwargs, expected_values)

        expected_values = ('5', '4', '3')
        iter_kwargs = dict(stop='2', reverse=True, include_value=False)
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
            it.next()

        it = db.iterator()
        with assert_raises(StopIteration):
            it.prev()
        with assert_raises(StopIteration):
            it.next()


def test_iterator_single_entry():
    with tmp_db('iterator_single_entry') as db:
        key = 'key'
        db.put(key, 'value')

        it = db.iterator(include_value=False)
        assert_equal(key, it.next())
        assert_equal(key, it.prev())
        assert_equal(key, it.next())
        assert_equal(key, it.prev())
        with assert_raises(StopIteration):
            it.prev()
        assert_equal(key, it.next())
        with assert_raises(StopIteration):
            it.next()
