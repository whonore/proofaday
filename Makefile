PACKAGE := proofaday

.PHONY: all format lint release clean

all:
	@echo 'Usage: make (format | lint | release | clean)'

format:
	black $(PACKAGE)
	isort $(PACKAGE)

lint:
	black --check $(PACKAGE)
	isort --check $(PACKAGE)
	mypy --show-error-codes -p $(PACKAGE)
	flake8 $(PACKAGE)
	pylint $(PACKAGE)

V := $(shell awk 'BEGIN { FS = "=" } /version/{ gsub("[ \"]", ""); print $$2 }' pyproject.toml)
release:
	git tag -a v$(V) -m "Release $(V)"

clean:
	rm -rf dist/
