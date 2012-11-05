
from nose.tools import assert_raises

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
    print db.put('foo', 'bar')


def test_get():
    print db.get('foo')

    assert_raises(TypeError, db.get, 1)
    assert_raises(TypeError, db.get, u'foo')
    assert_raises(TypeError, db.get, None)
