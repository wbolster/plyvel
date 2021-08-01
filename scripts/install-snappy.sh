#!/usr/bin/env bash
set -ex

SNAPPY_VERSION=1.1.9

SUDO=$(command -v sudo || true)
SCRIPT="$( cd "$( dirname $0 )" && pwd )"
PATCH_FILE=$SCRIPT/inline.patch # for snappy 1.1.9
echo $PATCH_FILE

# Check env
if [[ "$(uname)" == "Darwin" ]]; then
    ARCHS="x86_64"
    case "${CIBW_ARCHS_MACOS:-auto}" in
        "universal2")
            ARCHS="x86_64 arm64"
            ;;
        "arm64")
            ARCHS="arm64"
            ;;
        "x86_64")
            ARCHS="x86_64"
            ;;
        "auto")
            ;;
        *)
            echo "Unexpected arch: ${CIBW_ARCHS_MACOS}"
            exit 1
            ;;
    esac
    echo "building libsnappy for mac ${ARCHS}"
    for arch in ${ARCHS}; do
        export CFLAGS="-arch ${arch} ${CFLAGS:-}"
        export CXXFLAGS="-arch ${arch} ${CXXFLAGS:-}"
        export LDFLAGS="-arch ${arch} ${LDFLAGS:-}"
    done
fi

# Prepare snappy source code
mkdir -p ~/opt/snappy
cd ~/opt/snappy
curl -sL https://codeload.github.com/google/snappy/tar.gz/${SNAPPY_VERSION} | tar xzf -
cd ./snappy-*

# Patch snappy `inline`
cp $PATCH_FILE .
echo $PWD
patch < inline.patch

# Compile snappy

# `CMAKE_INSTALL_NAME_DIR` and `CMAKE_SKIP_INSTALL_RPATH` only have effect for MacOS
# [CMAKE_SKIP_RPATH/CMAKE_SKIP_INSTALL_RPATH and INSTALL_NAME_DIR precedence on macOS](https://gitlab.kitware.com/cmake/cmake/-/issues/16589)
# Set `INSTALL_NAME_DIR` to set the install name of shared library to be an absolute path instead of `@rpath/{target_name}`, which will help delocate the `wheel` 
# Or use `install_name_tool -change <old-path> <new-path> <file>` after .dylib was created

if [[ "$(uname)" == "Darwin" ]]; then
    INSTALL_NAME_DIR="/usr/local/lib"
fi

mkdir -p build && cd build
cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_SHARED_LIBS=ON \
    -DCMAKE_SKIP_INSTALL_RPATH=OFF \
    -DCMAKE_INSTALL_NAME_DIR=$INSTALL_NAME_DIR \
    -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
    -DSNAPPY_BUILD_BENCHMARKS=OFF \
    -DSNAPPY_BUILD_TESTS=OFF \
    ..

cmake --build . --target install

if [[ "$(uname)" == "Linux" ]]; then
    which ldconfig && ldconfig || true
fi

# Check snappy shared lib in macOS
if [[ "$(uname)" == "Darwin" ]]; then
    otool -L $INSTALL_NAME_DIR/libsnappy.dylib
    file $INSTALL_NAME_DIR/libsnappy.dylib
fi