
from nose.tools import (
    assert_equal,
    assert_is_none,
    assert_is_not_none,
    assert_raises)

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
    key = 'key-that-will-be-deleted'
    db.put(key, '')
    assert_is_not_none(db.get(key))
    db.delete(key)
    assert_is_none(db.get(key))


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
