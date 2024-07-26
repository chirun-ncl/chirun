PYTHON_COMMAND ?= python

test:
	$(PYTHON_COMMAND) -m unittest unittests

test_%:
	$(PYTHON_COMMAND) -m unittest unittests.$(patsubst test_%,%,$@)

keep_test_%:
	KEEP_TEST_OUTPUT=1 $(PYTHON_COMMAND) -m unittest unittests.$(patsubst keep_test_%,%,$@)

build:
	python -m build
