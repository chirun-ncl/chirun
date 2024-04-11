test:
	python -m unittest unittests

test_%:
	python -m unittest unittests.$(patsubst test_%,%,$@)
