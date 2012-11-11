
.PHONY: all clean test

all:
	cython --cplus plyvel.pyx
	python setup.py build_ext --inplace --force

clean:
	python setup.py clean
	$(RM) plyvel.cpp plyvel*.so
	$(RM) -r testdb/

test: all
	python $$(which nosetests) -v test_plyvel.py
