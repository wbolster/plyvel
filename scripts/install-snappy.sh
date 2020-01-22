#!/bin/sh

set -eux

SUDO=$(command -v sudo || true)

SNAPPY_VERSION=1.1.8

mkdir /opt/snappy
cd /opt/snappy
curl -sL https://codeload.github.com/google/snappy/tar.gz/${SNAPPY_VERSION} | tar xzf -
cd ./snappy-*
cmake -DBUILD_SHARED_LIBS=ON -DCMAKE_POSITION_INDEPENDENT_CODE=on .
cmake --build .
$SUDO "$(command -v cmake)" --build . --target install
$SUDO ldconfig
