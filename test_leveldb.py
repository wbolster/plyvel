
from nose.tools import assert_equal, assert_is_none, assert_raises

import leveldb
from leveldb import LevelDB

TEST_DB_DIR = 'db/'

db = None


def setup():
    global db
    db = LevelDB(TEST_DB_DIR)


def teardown():
    global db
    del db


def test_version():
    v = leveldb.__version__
    assert isinstance(v, basestring)
    assert v.startswith('1.')


# TODO: use different directories for open/close tests
# def test_open_close():
#     somedb = LevelDB(TEST_DB_DIR2)
#     print somedb
#     del somedb


def test_put():
    db.put('foo', 'bar')
    db.put('foo', 'bar', sync=False)
    db.put('foo', 'bar', sync=True)

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
