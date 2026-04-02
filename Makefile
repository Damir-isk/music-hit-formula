SHELL := /bin/bash

.PHONY: venv
venv:
	python3.14 -m venv .venv && \
		source .venv/bin/activate && \
		pip install -r requirements.txt

.PHONY: data
data:
	mkdir -p ./data/
	python3.14 -m venv .venv && \
		source .venv/bin/activate && \
		cd scripts && \
		python3.14 kworb_global_daily_totals.py
