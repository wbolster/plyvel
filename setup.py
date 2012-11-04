from setuptools import setup
from Cython.Build import cythonize

setup(name="leveldb-cython",
      version="0.1",
      author="Wouter Bolsterlee",
      author_email="uws@xs4all.nl",
      ext_modules=cythonize("leveldb.pyx"),
)
