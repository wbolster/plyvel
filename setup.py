from os.path import join, dirname
from setuptools import setup
from setuptools.extension import Extension
import platform
from Cython.Build import cythonize

CURRENT_DIR = dirname(__file__)

with open(join(CURRENT_DIR, 'plyvel/_version.py')) as fp:
    exec(fp.read(), globals(), locals())


def get_file_contents(filename):
    with open(join(CURRENT_DIR, filename)) as fp:
        return fp.read()

# add "-fno-rtti" fix `Symbol not found: __ZTIN7leveldb10ComparatorE` when using `leveldb 1.23`. Because `leveldb 1.23` compiled without RTTI(run time type info), if we use "-frtti", `U typeinfo for leveldb::Comparator` will not be found in `leveldb.a` or `leveldb.so`
extra_compile_args = ['-Wall', '-g', '-x', 'c++', '-std=c++11', '-fno-rtti']

if platform.system() == "Darwin":
    extra_compile_args += ["-stdlib=libc++"]

ext_modules = [
    Extension(
        'plyvel._plyvel',
        language="c++",
        sources=['plyvel/_plyvel.pyx', 'plyvel/comparator.cpp'],
        libraries=['leveldb'],
        extra_compile_args=extra_compile_args,
    ),
]

setup(
    name='plyvel-ci',
    description="Plyvel, a fast and feature-rich Python interface to LevelDB",
    long_description=get_file_contents('README.rst'),
    url="https://github.com/wbolster/plyvel",
    version=__version__,  # noqa: F821
    author="Wouter Bolsterlee",
    author_email="wouter@bolsterl.ee",
    ext_modules=cythonize(ext_modules, build_dir='build'),
    packages=['plyvel'],
    license="BSD License",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Programming Language :: C++",
        "Programming Language :: Cython",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Database",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
