#!/bin/sh

set -eux

git clean -xfd
make cython

if python --version | grep -q -F 3.8; then
    python setup.py sdist --dist-dir /output
fi
