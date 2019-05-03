#!/bin/sh

set -eux

SUDO=$(command -v sudo || true)

LEVELDB_VERSION=1.21

mkdir /opt/leveldb
cd /opt/leveldb
curl -sL leveldb.tar.gz https://codeload.github.com/google/leveldb/tar.gz/${LEVELDB_VERSION} | tar xzf -
cd leveldb-*
cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_SHARED_LIBS=ON \
    -DCMAKE_POSITION_INDEPENDENT_CODE=on \
    -DLEVELDB_BUILD_TESTS=off \
    -DLEVELDB_BUILD_BENCHMARKS=off \
    .
cmake --build .
$SUDO "$(command -v cmake)" --build . --target install
$SUDO ldconfig
