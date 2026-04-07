SHELL := /bin/bash

RUN_SCRIPT = python3.14 -m venv .venv && source .venv/bin/activate && cd scripts && python3.14

.PHONY: all
all: venv data

.PHONY: venv
venv:
	python3.14 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

.PHONY: data
data:
	$(RUN_SCRIPT) spotify_daily_chart_totals.py
