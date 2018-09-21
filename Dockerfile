# Dockerfile for building manylinux1 wheels.

FROM quay.io/pypa/manylinux1_x86_64

ENV LC_ALL=en_US.UTF-8

RUN true \
    && mkdir /opt/cmake \
    && cd /opt/cmake \
    && curl -o cmake.tar.gz https://cmake.org/files/v3.11/cmake-3.11.4.tar.gz \
    && tar xf cmake.tar.gz \
    && cd cmake-3.11.4 \
    && ./bootstrap \
    && make -j4 \
    && make install \
    && ldconfig

ENV SNAPPY_VERSION=1.1.7

RUN true \
    && mkdir /opt/snappy \
    && cd /opt/snappy \
    && curl -o snappy.tar.gz https://codeload.github.com/google/snappy/tar.gz/${SNAPPY_VERSION} \
    && tar xf snappy.tar.gz \
    && cd snappy-${SNAPPY_VERSION}/ \
    && cmake -DBUILD_SHARED_LIBS=ON -DCMAKE_POSITION_INDEPENDENT_CODE=on . \
    && make -j4 \
    && make install \
    && ldconfig

ENV LEVELDB_VERSION=1.20

RUN true \
    && mkdir /opt/leveldb \
    && cd /opt/leveldb \
    && curl -o leveldb.tar.gz https://codeload.github.com/google/leveldb/tar.gz/v${LEVELDB_VERSION} \
    && tar xf leveldb.tar.gz \
    && cd leveldb-${LEVELDB_VERSION}/ \
    && make -j4 \
    && cp -av out-static/lib* out-shared/lib* /usr/local/lib/ \
    && cp -av include/leveldb/ /usr/local/include/ \
    && ldconfig

ENV PATH="/opt/python/cp37-cp37m/bin:${PATH}"

RUN pip install --upgrade pip setuptools tox cython

ENV PROJECT_ROOT="/opt/plyvel"

COPY . $PROJECT_ROOT

WORKDIR $PROJECT_ROOT

CMD true \
    && git clean -xfd \
    && make sdist wheels
