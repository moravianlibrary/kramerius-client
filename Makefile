.PHONY: create-env rm-env

create-env:
	python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

rm-env:
	rm -r .venv/

