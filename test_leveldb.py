
from nose.tools import assert_raises

import leveldb
from leveldb import LevelDB

DB_DIR = 'db/'


def test_version():
    v = leveldb.__version__
    assert isinstance(v, basestring)
    assert v.startswith('1.')


def test_open():
    db = LevelDB(DB_DIR)
    print db


def test_close():
    db = LevelDB(DB_DIR)
    del db


def test_put():
    db = LevelDB(DB_DIR)
    print db.put('foo', 'bar')


def test_get():
    db = LevelDB(DB_DIR)
    print db.get('foo')

    with assert_raises(TypeError):
        print db.get('foo', 'bar')
