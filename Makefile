PACKAGE := proofaday

.PHONY: all format lint upload clean

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

V := $(shell awk 'BEGIN { FS = "=" } /version=/{ gsub("[,\"]", ""); print $$2 }' setup.py)
release:
	git tag -a v$(V) -m "Release $(V)"

clean:
	rm -rf build/ dist/ $(PACKAGE).egg-info/
