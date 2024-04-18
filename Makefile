test:
	python -m unittest unittests

test_%:
	python -m unittest unittests.$(patsubst test_%,%,$@)

keep_test_%:
	KEEP_TEST_OUTPUT=1 python -m unittest unittests.$(patsubst keep_test_%,%,$@)
