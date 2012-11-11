
.PHONY: all doc clean test

all:
	cython --cplus plyvel.pyx
	python setup.py build_ext --inplace --force

doc:
	python setup.py build_sphinx
	@echo
	@echo Generated documentation: "file://"$$(readlink -f doc/build/html/index.html)
	@echo

clean:
	python setup.py clean
	$(RM) plyvel.cpp plyvel*.so
	$(RM) -r testdb/

test: all
	python $$(which nosetests) -v test_plyvel.py
