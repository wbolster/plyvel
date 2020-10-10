======
Plyvel
======

**Plyvel** is a fast and feature-rich Python interface to LevelDB_.

.. _LevelDB: http://code.google.com/p/leveldb/

Plyvel's key features are:

* **Rich feature set**

  Plyvel wraps most of the LevelDB C++ API and adds some features of its own. In
  addition to basic features like getting, putting and deleting data, Plyvel
  allows you to use write batches, database snapshots, very flexible iterators,
  prefixed databases, bloom filters, custom cache sizes, custom comparators, and
  other goodness LevelDB has to offer.

* **Friendly Pythonic API**

  Plyvel has a friendly and well-designed API that uses Python idioms like
  iterators and context managers (``with`` blocks), without sacrificing the
  power or performance of the underlying LevelDB C++ API.

* **High performance**

  Plyvel executes all performance-critical code at C speed (using Cython_),
  which means Plyvel is a good fit for high performance applications.

  .. _Cython: http://cython.org/

* **Extensive documentation**

  Plyvel comes with extensive documentation, including a user guide and API
  reference material.


.. note Do you like Plyvel?

You should know that Plyvel is a hobby project, written and maintained by me,
Wouter Bolsterlee, in my spare time. Please consider making a small donation_ to
let me know you appreciate my work. Thanks!

.. _donation: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=4FF4VZ5LTJ73N


.. rubric:: Documentation contents

.. toctree::
   :maxdepth: 2

   installation
   user
   api
   news
   developer
   license


.. rubric:: External links

* `Online documentation <https://plyvel.readthedocs.io/>`_ (Read the docs)
* `Project page <https://github.com/wbolster/plyvel>`_ with source code and
  issue tracker (Github)
* `Python Package Index (PyPI) page <http://pypi.python.org/pypi/plyvel/>`_ with
  released tarballs
