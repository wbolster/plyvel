
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

db = None


def setup():
    global db
    db = DB(TEST_DB_DIR)


def teardown():
    global db
    del db


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
    db.put('foo', 'bar')
    db.put('foo', 'bar', sync=False)
    db.put('foo', 'bar', sync=True)

    for i in xrange(100000):
        key = 'key-%d' % i
        value = 'value-%d' % i
        db.put(key, value)

    assert_raises(TypeError, db.put, 'foo', 12)
    assert_raises(TypeError, db.put, 12, 'foo')


def test_get():
    assert_equal('bar', db.get('foo'))
    assert_equal('bar', db.get('foo', verify_checksums=True))
    assert_equal('bar', db.get('foo', verify_checksums=False))
    assert_equal('bar', db.get('foo', verify_checksums=None))
    assert_equal('bar', db.get('foo', fill_cache=True))
    assert_equal('bar', db.get('foo', fill_cache=False, verify_checksums=None))

    assert_is_none(db.get('key-that-does-not-exist'))

    assert_raises(TypeError, db.get, 1)
    assert_raises(TypeError, db.get, u'foo')
    assert_raises(TypeError, db.get, None)

    assert_raises(TypeError, db.get, 'foo', True)


def test_delete():
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
    for key, value in db:
        print key, value


@nottest
def test_manual_iteration(db, iter_kwargs, expected_values):
    it = db.range_iter(**iter_kwargs)
    first, second, third = expected_values

    assert_equal(first, next(it))
    assert_equal(second, next(it))
    assert_equal(third, it.next())
    with assert_raises(StopIteration):
        next(it)


@nottest
def test_iterator_single_step(db, iter_kwargs, expected_values):
    it = db.range_iter(**iter_kwargs)
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
    it = db.range_iter(**iter_kwargs)
    first, second, third = expected_values

    # End of iterator
    it.end()
    with assert_raises(StopIteration):
        it.next()
    assert_equal(third, it.prev())

    # Begin of iterator
    it.begin()
    with assert_raises(StopIteration):
        it.prev()
    assert_equal(first, next(it))


def test_forward_iteration():
    expected_values = ('1', '2', '3')
    iter_kwargs = dict()
    test_manual_iteration(db, iter_kwargs, expected_values)
    test_iterator_single_step(db, iter_kwargs, expected_values)
    test_iterator_extremes(db, iter_kwargs, expected_values)


def test_backward_iteration():
    expected_values = ('3', '2', '1')
    iter_kwargs = dict(reverse=True)
    test_manual_iteration(db, iter_kwargs, expected_values)
    test_iterator_single_step(db, iter_kwargs, expected_values)
    test_iterator_extremes(db, iter_kwargs, expected_values)


def test_range_iteration():
    # TODO: use a database containing ['1', '2', '3', '4', '5'] keys

    assert_list_equal(
        ['2', '3', '4', '5'],
        list(db.range_iter(start='2')))

    assert_list_equal(
        ['1', '2'],
        list(db.range_iter(stop='3')))

    assert_list_equal(
        ['1', '2'],
        list(db.range_iter(start='0', stop='3')))

    assert_list_equal([], list(db.range_iter(start='3', stop='0')))

    expected_values = ('2', '3', '4')
    test_manual_iteration(db, dict(start='2', stop='5'), expected_values)
    test_iterator_single_step(db, dict(start='2', stop='5'), expected_values)
    test_iterator_extremes(db, dict(start='2', stop='5'), expected_values)

    expected_values = ('5', '4', '3')
    test_manual_iteration(db, dict(stop='2', reverse=True), expected_values)
    test_iterator_single_step(db, dict(stop='2', reverse=True), expected_values)
    test_iterator_extremes(db, dict(stop='2', reverse=True), expected_values)


def test_range_empty_database():
    empty_db = db  # FIXME: actually use an empty database

    it = empty_db.range_iter()
    it.begin()  # no-op (don't crash)
    it.end()  # no-op (don't crash)

    it = empty_db.range_iter()
    with assert_raises(StopIteration):
        it.next()

    it = empty_db.range_iter()
    with assert_raises(StopIteration):
        it.prev()
    with assert_raises(StopIteration):
        it.next()

