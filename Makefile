PACKAGE := proofaday

.PHONY: all format lint upload clean

all:
	@echo 'Usage: make (format | lint | upload | clean)'

format:
	black $(PACKAGE)
	isort $(PACKAGE)

lint:
	black --check $(PACKAGE)
	isort --check $(PACKAGE)
	mypy --show-error-codes -p $(PACKAGE)
	flake8 $(PACKAGE)

upload:
	python setup.py sdist bdist_wheel
	twine upload --skip-existing dist/*

clean:
	rm -r build/ dist/ $(PACKAGE).egg-info/
