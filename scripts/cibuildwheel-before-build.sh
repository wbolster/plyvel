#!/bin/sh

set -eux

python --version
cython --version

git clean -xfd
make cython

if python --version | grep -q -F 3.12; then
    python setup.py sdist --dist-dir /output
fi
