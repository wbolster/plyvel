
.PHONY: all ext doc clean test

all: ext

ext:
	@echo
	@echo "Building extension"
	@echo "=================="
	@echo
	cython --cplus --fast-fail --annotate plyvel/_plyvel.pyx
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
	python $$(which nosetests) -v $(TESTS)
