.PHONY: all cython ext doc clean test wheels

all: cython ext

cython:
	@echo
	@echo "Running Cython"
	@echo "=============="
	@echo
	cython --version
	cython --cplus --fast-fail --annotate plyvel/_plyvel.pyx

ext: cython
	@echo
	@echo "Building extension"
	@echo "=================="
	@echo
	python setup.py build_ext --inplace --force

doc:
	@echo
	@echo "Building documentation"
	@echo "======================"
	@echo
	python setup.py build_sphinx
	@echo
	@echo Generated documentation: "file://"$$(readlink -f doc/build/html/index.html)
	@echo

clean:
	@echo
	@echo "Cleaning generated files"
	@echo "========================"
	@echo
	python setup.py clean
	$(RM) plyvel/_plyvel.cpp plyvel/_plyvel*.so
	$(RM) -r testdb/
	$(RM) -r doc/build/
	$(RM) -r plyvel.egg-info/
	find . -name '*.py[co]' -delete
	find . -name __pycache__ -delete

test: ext
	@echo
	@echo "Running tests"
	@echo "============="
	@echo
	py.test

wheels: cython
	# Note: this should run inside the docker container.
	@echo
	@echo "Building wheels"
	@echo "==============="
	@echo
	for dir in /opt/python/*; do \
		$${dir}/bin/python setup.py bdist_wheel; \
	done
	for wheel in dist/*.whl; do \
		auditwheel show $${wheel}; \
		auditwheel repair -w /wheelhouse/ $${wheel}; \
	done
