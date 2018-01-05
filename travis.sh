#!/bin/sh

set -e -u -x

LEVELDB_VERSION=1.20

wget https://github.com/google/leveldb/archive/v${LEVELDB_VERSION}.tar.gz
tar xf v${LEVELDB_VERSION}.tar.gz
cd leveldb-${LEVELDB_VERSION}/
make
sudo cp -av out-static/lib* out-shared/lib* /usr/local/lib/
sudo cp -av include/leveldb/ /usr/local/include/
sudo ldconfig
