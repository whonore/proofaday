PACKAGE := proofaday

.PHONY: all format lint patch minor major clean

all:
	@echo 'Usage: make (format | lint | patch | minor | major | clean)'

format:
	black $(PACKAGE)
	isort $(PACKAGE)

lint:
	black --check $(PACKAGE)
	isort --check $(PACKAGE)
	mypy --show-error-codes -p $(PACKAGE)
	flake8 $(PACKAGE)
	pylint $(PACKAGE)

patch: lint
	bump2version $@

minor: lint
	bump2version $@

major: lint
	bump2version $@

clean:
	rm -rf dist/
