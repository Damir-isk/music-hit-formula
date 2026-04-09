SHELL := /bin/bash

.PHONY: all
all: venv

.PHONY: venv
venv:
	python3.14 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

.PHONY: archive
archive:
	zip -rFS data.zip data
	zip -rFS logs.zip logs

.PHONY: unarchive
unarchive:
	unzip -o data.zip
	unzip -o logs.zip
