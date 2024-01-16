FROM quay.io/pypa/manylinux2014_x86_64

# Remove sudo executable, since it does not work at all.
# The installation scripts will not to invoke it.
RUN rm "$(which sudo)"

COPY scripts/ .

RUN yum update && yum install -y lzo-devel lz4-devel
RUN ./install-snappy.sh
RUN ./install-leveldb.sh

ENV PATH="/opt/python/cp39-cp39/bin:${PATH}"

RUN pip install --upgrade pip setuptools cython
