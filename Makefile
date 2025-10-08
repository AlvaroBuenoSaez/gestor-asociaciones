.DEFAULT_GOAL := all
.PHONY: help show-commands

help: show-commands

show-commands:
	@echo "Run the commands below manually (copy & paste):"
	@echo ""
	@echo "# 1) Create and activate virtualenv"
	@echo "python -m venv .venv"
	@echo "source .venv/bin/activate"
	@echo ""
	@echo "# 2) Install dependencies"
	@echo "pip install -r requirements.txt"
	@echo ""
	@echo "# 3) Apply migrations"
	@echo "python manage.py migrate"
	@echo ""
	@echo "# 4) Create superuser (interactive)"
	@echo "python manage.py createsuperuser"
	@echo ""
	@echo "# 5) Create sample associations and user"
	@echo ".venv/bin/python create_sample_associations.py"
	@echo ""
	@echo "# 6) (Optional) Import socias into 'Asociación Vecinal Lucero' (dry-run recommended first):"
	@echo ".venv/bin/python create_sample_associations.py --import-socias --asociacion-registro AV004 --dry-run"
	@echo ""
	@echo "# 7) (Optional) Import activities, projects and financial data:"
	@echo ".venv/bin/python .migrations/import_avlucero_data.py --asociacion_id 4 --dry-run"
	@echo ""
	@echo "# You can remove the --dry-run flag to perform the real import."
	@echo ""

.PHONY: all init migrate createsuper seed import-activities import-activities-dry clean

PYTHON ?= python3
VENV := .venv
PY := $(VENV)/bin/python

all: init migrate createsuper seed import-activities

init:
	@echo "==> Creating virtualenv (if missing)"
	@if [ ! -d "$(VENV)" ]; then \
		$(PYTHON) -m venv $(VENV); \
		echo "Virtualenv created at $(VENV)"; \
	else \
		echo "Virtualenv already exists: $(VENV)"; \
	fi
	@echo "==> Installing requirements"
	@$(PY) -m pip install --upgrade pip setuptools wheel >/dev/null
	@$(PY) -m pip install -r requirements.txt

migrate: init
	@echo "==> Applying migrations"
	@$(PY) manage.py migrate

createsuper: migrate
	@echo "==> Creating superuser 'admin' (password: admin) if not exists"
	@$(PY) scripts/create_admin.py

seed: createsuper
	@echo "==> Creating sample associations and importing socias into 'Asociación Vecinal Lucero' (AV004)"
	@$(PY) create_sample_associations.py --import-socias --asociacion-registro AV004

import-activities: seed
	@echo "==> Importing activities, projects, and financial data into 'Asociación Vecinal Lucero'"
	@$(PY) .migrations/import_avlucero_data.py --asociacion_id 4

import-activities-dry: seed
	@echo "==> [DRY-RUN] Checking what activities, projects, and financial data would be imported"
	@$(PY) .migrations/import_avlucero_data.py --asociacion_id 4 --dry-run

clean:
	@echo "==> Clean: (does not remove venv)"
	@echo "No-op"

