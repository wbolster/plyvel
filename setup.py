from os.path import join, dirname
from setuptools import setup
from setuptools.extension import Extension

CURRENT_DIR = dirname(__file__)

with open(join(CURRENT_DIR, 'plyvel/_version.py')) as fp:
    exec(fp.read(), globals(), locals())


def get_file_contents(filename):
    with open(join(CURRENT_DIR, filename)) as fp:
        return fp.read()

ext_modules = [
    Extension(
        'plyvel._plyvel',
        sources=['plyvel/_plyvel.cpp', 'plyvel/comparator.cpp'],
        libraries=['leveldb'],
        extra_compile_args=['-Wall', '-g'],
    )
]

setup(
    name='plyvel',
    description="Plyvel, a fast and feature-rich Python interface to LevelDB",
    long_description=get_file_contents('README.rst'),
    url="https://github.com/wbolster/plyvel",
    version=__version__,
    author="Wouter Bolsterlee",
    author_email="uws@xs4all.nl",
    ext_modules=ext_modules,
    packages=['plyvel'],
    license="BSD License",
    classifiers=[
        "Development Status :: 4 - Beta",
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
