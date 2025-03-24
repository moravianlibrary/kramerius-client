PYTHON_BASE := python3.12
PYTHON_VENV := .venv
PYTHON := $(PYTHON_VENV)/bin/python
PYTHON_PIP := $(PYTHON_VENV)/bin/pip
PYTHON_DEPS := requirements.txt

.PHONY: generate-env remove-env regenerate-env publish

generate-env:
	$(PYTHON_BASE) -m venv $(PYTHON_VENV)
	$(PYTHON) -m ensurepip
	$(PYTHON_PIP) install --upgrade pip
	$(PYTHON_PIP) install -r $(PYTHON_DEPS)

remove-env:
	rm -rf $(PYTHON_VENV)

regenerate-env: remove-env generate-env

publish:
	$(PYTHON) setup.py sdist bdist_wheel && twine upload dist/*
