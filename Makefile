PACKAGE_NAME := 'sepal'
PY_FILES := $(shell find $(PACKAGE_NAME) -name \*.py)
SRC_FILES := $(PY_FILES)
VENV_BIN := venv/bin

GIT_DIRTY := $(shell git diff)
GIT_HASH := $(shell git rev-parse --short HEAD)

check-git-dirty:
ifneq ($(GIT_DIRTY),)
	@echo "ERROR: Your git working tree is dirty. Exiting..."
	@exit 1
endif

venv: # requirements/dev.txt
	python3 -m venv venv
	$(VENV_BIN)/pip install -U pip
#	$(VENV_BIN)/pip install -r requirements/dev.txt
	touch $@ # update timestamp in case the folder already existed

test:
	tox -q

update-deps:
	$(VENV_BIN)/pip-compile requirements/dev.in
	$(VENV_BIN)/pip-compile requirements/prod.in
	$(VENV_BIN)/pip-sync requirements/dev.txt

.PHONY: test check-git-dirty update-deps
