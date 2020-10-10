#!/bin/sh

set -eux

git clean -xfd
make cython

if python --version | grep -q -F 3.9; then
    python setup.py sdist --dist-dir /output
fi
