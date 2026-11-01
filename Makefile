.PHONY: help lint validate check-experiment-math check-drafts bundle-drafts check-generated build provision compile security ci bundle papers check-papers arxiv check-arxiv retrospective check-retrospective
.DEFAULT_GOAL := help

# Prefer the virtual environment from the documented setup, so make works
# without activating it.
PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
TOOL = PYTHONPATH=src $(PYTHON) -m curious_signals
RUFF = $(PYTHON) -m ruff

help:
	@echo "Targets:"
	@echo "  lint     - Ruff lint + format check, shellcheck"
	@echo "  validate - Validate XML and phyphox files"
	@echo "  check-experiment-math - Replay scientific XML and missing-data regression fixtures"
	@echo "  check-drafts - Check draft coverage, XML, and numerical/recording fixtures"
	@echo "  bundle-drafts - Package draft experiments and companions in output/drafts/"
	@echo "  check-generated - Verify tracked experiments match their sources"
	@echo "  build    - Rebuild experiments/*.phyphox from src/phyphox/*.phyphox.xml"
	@echo "  provision - Install pinned Arduino core and libraries (network)"
	@echo "  compile  - Verify installed pins and compile Arduino sketch (no installs/upload)"
	@echo "  security - Credential scan of tracked and untracked files"
	@echo "  ci       - Run every gate; provisions Arduino packages (network), never rewrites tracked files"
	@echo "  bundle   - Build and zip the seven core sensor experiments"
	@echo "  papers   - Build 21 final papers, paginated retrospective, and source archives"
	@echo "  check-papers - Check manuscript coverage, references, and source hashes"
	@echo "  arxiv    - Prepare and independently compile 21 arXiv submission packages"
	@echo "  check-arxiv - Check arXiv sources, PDF proofs and upload archives"
	@echo "  retrospective - Assemble the retrospective from the verified arXiv papers"
	@echo "  check-retrospective - Check collection sources, pagination, links and archives"

lint:
	$(RUFF) check .
	$(RUFF) format --check .
	shellcheck scripts/*.sh

validate:
	$(TOOL) validate
	$(PYTHON) scripts/check_experiment_math.py
	$(PYTHON) scripts/check_drafts.py
	$(PYTHON) scripts/check_doc_links.py

check-experiment-math:
	$(PYTHON) scripts/check_experiment_math.py

check-drafts:
	$(PYTHON) scripts/check_drafts.py

bundle-drafts: check-drafts
	$(PYTHON) scripts/bundle_drafts.py

check-generated:
	$(TOOL) check-generated

build:
	$(TOOL) build

compile:
	$(TOOL) compile

provision:
	$(TOOL) provision

security:
	bash scripts/secret-scan.sh

ci:
	+$(MAKE) --no-print-directory lint
	+$(MAKE) --no-print-directory validate
	+$(MAKE) --no-print-directory check-generated
	+$(MAKE) --no-print-directory provision
	+$(MAKE) --no-print-directory compile
	+$(MAKE) --no-print-directory security

bundle:
	$(TOOL) bundle

papers:
	$(PYTHON) docs/papers/build.py

check-papers:
	$(PYTHON) docs/papers/build.py --check

arxiv: check-papers
	$(PYTHON) docs/papers/prepare_arxiv.py

check-arxiv:
	$(PYTHON) docs/papers/prepare_arxiv.py --check

retrospective: check-arxiv
	$(PYTHON) docs/papers/build_retrospective.py

check-retrospective: check-arxiv
	$(PYTHON) docs/papers/build_retrospective.py --check
