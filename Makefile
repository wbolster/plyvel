
.PHONY: all ext doc clean test

all: ext doc test

ext:
	cython --cplus --fast-fail plyvel.pyx
	python setup.py build_ext --inplace --force

doc: ext
	python setup.py build_sphinx
	@echo
	@echo Generated documentation: "file://"$$(readlink -f doc/build/html/index.html)
	@echo

clean:
	python setup.py clean
	$(RM) plyvel.cpp plyvel*.so
	$(RM) -r testdb/

test: ext
	python $$(which nosetests) -v -s
