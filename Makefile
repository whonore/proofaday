PACKAGE := proofaday

.PHONY: all lint upload clean

all:
	@echo 'Usage: make (lint | upload | clean)'

lint:
	black $(PACKAGE)
	isort $(PACKAGE)
	mypy --show-error-codes -p $(PACKAGE)
	flake8 $(PACKAGE)

upload:
	python setup.py sdist bdist_wheel
	twine upload --skip-existing dist/*

clean:
	rm -r build/ dist/ $(PACKAGE).egg-info/
