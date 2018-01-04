#!/bin/sh

set -e -u -x

LEVELDB_VERSION=1.20

wget https://github.com/google/leveldb/archive/v${LEVELDB_VERSION}.tar.gz
tar xf v${LEVELDB_VERSION}.tar.gz
cd leveldb-${LEVELDB_VERSION}/
make

# based on https://gist.github.com/dustismo/6203329
sudo scp -r out-static/lib* out-shared/lib* /usr/local/lib/
cd include/
sudo scp -r leveldb /usr/local/include/
sudo ldconfig
