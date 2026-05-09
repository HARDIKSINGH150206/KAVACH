VENV ?= kavach-env
PYTHON ?= $(VENV)/bin/python
NPM ?= npm

.PHONY: install install-dev frontend test lint format docker-build compose-up start stop status readiness profile-demo profile-pilot profile-prod pilot-gate

install:
	python -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

install-dev: install
	$(PYTHON) -m pip install -e ".[dev]"
	$(PYTHON) -m pip install pre-commit
	$(PYTHON) -m pip install uvicorn[standard]
	$(NPM) --prefix frontend install
	$(PYTHON) -m pre_commit install

frontend:
	$(NPM) --prefix frontend install

test:
	$(PYTHON) -m pytest tests/ -v

frontend-test:
	cd frontend && $(NPM) run test

lint:
	$(PYTHON) -m pre_commit run --all-files

format:
	$(PYTHON) -m black .
	$(PYTHON) -m isort .

docker-build:
	docker build -t kavach-backend .

compose-up:
	docker compose up --build

start:
	$(PYTHON) -m backend.cli start

stop:
	$(PYTHON) -m backend.cli stop

status:
	$(PYTHON) -m backend.cli status

readiness:
	$(PYTHON) scripts/check_readiness.py

profile-demo:
	./scripts/run_profile.sh demo

profile-pilot:
	./scripts/run_profile.sh pilot

profile-prod:
	./scripts/run_profile.sh prod

pilot-gate:
	$(PYTHON) scripts/pilot_gate.py
