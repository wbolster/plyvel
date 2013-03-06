
.PHONY: all ext doc clean test

all: ext doc test

ext:
	cython --cplus --fast-fail plyvel/_plyvel.pyx
	python setup.py build_ext --inplace --force

doc:
	python setup.py build_sphinx
	@echo
	@echo Generated documentation: "file://"$$(readlink -f doc/build/html/index.html)
	@echo

clean:
	python setup.py clean
	$(RM) plyvel/_plyvel.cpp plyvel/_plyvel*.so
	$(RM) -r testdb/
	$(RM) -r doc/build/
	$(RM) -r plyvel.egg-info/
	find . -name '*.py[co]' -delete
	find . -name __pycache__ -delete

test: ext
	python $$(which nosetests) -v $(TESTS)

dist: clean ext doc test
	python setup.py sdist
