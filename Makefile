PACKAGE_NAME := 'sepal'
PY_FILES := $(shell find $(PACKAGE_NAME) -name \*.py)
SRC_FILES := $(PY_FILES)
VENV_BIN := venv/bin

GIT_DIRTY := $(shell git diff)
GIT_HASH := $(shell git rev-parse --short HEAD)
PYTHONPATH := .

.PHONY: db\:init db\:migrate db\:upgrade deps\:update server\:start test check-git-dirty

check-git-dirty:
ifneq ($(GIT_DIRTY),)
	@echo "ERROR: Your git working tree is dirty. Exiting..."
	@exit 1
endif

# TODO: require python 3.8
venv: requirements/dev.txt
	python3 -m venv venv
	$(VENV_BIN)/pip install -U pip pip-tools
	$(VENV_BIN)/pip install -r requirements/dev.txt
	touch $@ # update timestamp in case the folder already existed

test:
	tox -q

deps\:install:
	$(VENV_BIN)/pip-sync requirements/dev.txt

deps\:update:
	$(VENV_BIN)/pip-compile requirements/lint.in
	$(VENV_BIN)/pip-compile requirements/dev.in
	$(VENV_BIN)/pip-compile requirements/prod.in
	make deps:install

db\:init:
	@echo init db...

db\:migrate:
	@echo generating migrations...
	PYTHONPATH=. alembic -c migrations/alembic.ini revision --autogenerate $*

db\:upgrade:
	@echo upgrading...
	alembic -c migrations/alembic.ini upgrade head

server\:start:
	uvicorn sepal.app:app --reload

