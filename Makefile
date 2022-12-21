.ONESHELL:
ENV_PREFIX=$(shell python -c "if __import__('pathlib').Path('.venv/bin/pip').exists(): print('.venv/bin/')")

.PHONY: help
help:              ## Show the help.
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep


.PHONY: show
show:              ## Show the current environment.
	@echo "Current environment:"
	@echo "Running using $(ENV_PREFIX)"
	@$(ENV_PREFIX)python -V
	@$(ENV_PREFIX)python -m site

.PHONY: doc
doc:              ## Clean generated docs and compile fresh ones.
	$(MAKE) -C docs/ clean
	$(MAKE) -C docs/ html

.PHONY: black
black:             ## Format code using black.
	$(ENV_PREFIX)black -l 99 sidcon/ tests/

.PHONY: blackcheck
blackcheck:        ## Check code format using black.
	$(ENV_PREFIX)black -l 99 sidcon/ tests/ --check

.PHONY: isort
isort:             ## Format code using isort.
	$(ENV_PREFIX)isort --line-length 99 sidcon/

.PHONY: autoflake
autoflake:         ## Remove unused imports using autoflake.
	$(ENV_PREFIX)autoflake -ri sidcon/ tests/

.PHONY: autoflakeall
autoflakeall:         ## Remove all unused imports using autoflake.
	$(ENV_PREFIX)autoflake --remove-all-unused-imports -ri sidcon/ tests/

.PHONY: fmt
fmt: isort black autoflake  ## Format code using isort, black, and autoflake.

.PHONY: flake
flake:             ## Run pep8 linter.
	$(ENV_PREFIX)flake8 --extend-ignore=E731 --max-line-length 99 sidcon/ tests/

.PHONY: lint
lint: flake blackcheck  ## Run pep8 linter and black.

.PHONY: mypy
mypy:              ## Run mypy type checker.
	$(ENV_PREFIX)python -m mypy --ignore-missing-imports sidcon/

.PHONY: check
check: lint mypy   ## Run all linters and mypy.

.PHONY: cov
cov:               ## Run tests and produce coverage reports if successful.
	@if $(ENV_PREFIX)pytest -vv --cov-config .coveragerc --cov-report term-missing --cov=sidcon -l --tb=short --maxfail=1 tests/; \
	then \
		:; \
	else \
		exit $?; \
	fi
	$(ENV_PREFIX)coverage xml
	$(ENV_PREFIX)coverage html

.PHONY: test
test:              ## Run tests and generate coverage report.
	$(ENV_PREFIX)pytest -vv	-l --tb=short tests/

.PHONY: proof
proof: check cov  ## ("Proofread") Run all linters, mypy, and unit tests.

.PHONY: watch
watch:             ## Run tests on every change.
	ls **/**.py | entr $(ENV_PREFIX)pytest -s -vvv -l --tb=long tests/

.PHONY: clean
clean:             ## Clean unused files.
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name '__pycache__' -exec rm -rf {} \;
	@find ./ -name 'Thumbs.db' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;
	@rm -rf .cache
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -rf build
	@rm -rf dist
	@rm -rf *.egg-info
	@rm -rf htmlcov
	@rm -rf .tox/

.PHONY: virtualenv
virtualenv:        ## Create a virtual environment.
	@echo "creating virtualenv ..."
	@rm -rf .venv
	@python3 -m venv .venv
	@./.venv/bin/pip install -U pip
	@./.venv/bin/pip install -e .[test]
	@echo
	@echo "!!! Please run 'source .venv/bin/activate' to enable the environment !!!"
