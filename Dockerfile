# Dockerfile for building manylinux1 wheels.
#
# Usage:
#
#   docker build -t plyvel-build .
#   docker run -i -t -v $(pwd)/dist/:/wheelhouse plyvel-build
#
# The .whl files should appear in dist/ on the host.

FROM quay.io/pypa/manylinux1_x86_64

ENV LC_ALL=en_US.UTF-8
ENV LEVELDB_VERSION=1.20
ENV PATH="/opt/python/cp36-cp36m/bin:${PATH}"
ENV PROJECT_ROOT="/opt/plyvel"

RUN true \
    && mkdir /opt/leveldb \
    && cd /opt/leveldb \
    && wget -O leveldb.tar.gz https://github.com/google/leveldb/archive/v${LEVELDB_VERSION}.tar.gz \
    && tar xf leveldb.tar.gz \
    && cd leveldb-${LEVELDB_VERSION}/ \
    && make -j4 \
    && cp -av out-static/lib* out-shared/lib* /usr/local/lib/ \
    && cp -av include/leveldb/ /usr/local/include/ \
    && ldconfig

RUN pip install --upgrade pip setuptools tox cython

COPY . $PROJECT_ROOT

WORKDIR $PROJECT_ROOT

CMD true \
    && git clean -xfd \
    && make wheels
