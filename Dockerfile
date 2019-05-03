FROM quay.io/pypa/manylinux1_x86_64

# Use CMake < 3.14.x b/c https://gitlab.kitware.com/cmake/cmake/issues/19086
ENV CMAKE_VERSION=3.13.4

RUN true \
    && mkdir /opt/cmake \
    && cd /opt/cmake \
    && curl -sL https://github.com/Kitware/CMake/releases/download/v${CMAKE_VERSION}/cmake-${CMAKE_VERSION}.tar.gz | tar xzf - \
    && cd ./cmake-* \
    && ./bootstrap --parallel=4 \
    && make -j4 \
    && make install

# Remove sudo executable, since it does not work at all.
# The installation scripts will not to invoke it.
RUN rm "$(which sudo)"

COPY scripts/install-snappy.sh .
RUN ./install-snappy.sh

COPY scripts/install-leveldb.sh .
RUN ./install-leveldb.sh

ENV PATH="/opt/python/cp37-cp37m/bin:${PATH}"

RUN pip install --upgrade pip setuptools cython
