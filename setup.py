from os.path import join, dirname
from setuptools import setup
from setuptools.extension import Extension

CURRENT_DIR = dirname(__file__)

execfile(join(CURRENT_DIR, 'plyvel/_version.py'))

ext_modules = [
    Extension(
        'plyvel._plyvel',
        ['plyvel/_plyvel.cpp'],
        libraries=['leveldb'])
]

setup(
    name='plyvel',
    version=__version__,
    author="Wouter Bolsterlee",
    author_email="uws@xs4all.nl",
    ext_modules=ext_modules,
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
