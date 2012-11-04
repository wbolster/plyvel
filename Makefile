
.PHONY: all clean test

all:
	cython --cplus leveldb.pyx
	python setup.py build_ext --inplace --force

clean:
	python setup.py clean
	$(RM) leveldb.cpp leveldb.so

test:
	python $$(which nosetests) -v test_leveldb.py
