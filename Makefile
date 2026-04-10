SHELL := /bin/bash

.PHONY: all
all: venv

.PHONY: venv
venv:
	python3.14 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
