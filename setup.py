from setuptools import setup
from setuptools.extension import Extension

ext_modules = [
    Extension(
        'plyvel',
        ['plyvel.cpp'],
        libraries=['leveldb'])
]

setup(
    name='plyvel',
    version='0.1dev',
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
