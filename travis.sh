#!/bin/sh

set -e -u -x

LEVELDB_VERSION=1.20

wget https://github.com/google/leveldb/archive/v${LEVELDB_VERSION}.tar.gz
tar xf v${LEVELDB_VERSION}.tar.gz
cd leveldb-${LEVELDB_VERSION}/
make
sudo make install
