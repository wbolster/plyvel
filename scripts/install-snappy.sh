#!/bin/sh

set -eux

SUDO=$(command -v sudo || true)

SNAPPY_VERSION=1.2.0

mkdir /opt/snappy
cd /opt/snappy
curl -sL https://codeload.github.com/google/snappy/tar.gz/${SNAPPY_VERSION} | tar xzf -
cd ./snappy-*

# See https://github.com/google/snappy/blob/${SNAPPY_VERSION}/.gitmodules
git clone --depth 1 \
    https://github.com/google/benchmark.git third_party/benchmark
git clone --depth 1 \
    https://github.com/google/googletest.git third_party/googletest

cmake -DBUILD_SHARED_LIBS=ON -DCMAKE_POSITION_INDEPENDENT_CODE=on .
cmake --build .
$SUDO "$(command -v cmake)" --build . --target install
$SUDO ldconfig
