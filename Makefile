# ═════════════════════════════════════════════════════════════════════════════
#  ESPPA - Makefile
#  Common commands for development.
# ═════════════════════════════════════════════════════════════════════════════

.PHONY: help install migrate run test shell superuser seed clean check

help: ## Display this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

setup: install migrate seed ## One-command setup: install + migrate + seed data

migrate: ## Run database migrations
	python src/manage.py migrate

makemigrations: ## Create new migrations
	python src/manage.py makemigrations

run: ## Run development server
	python src/manage.py runserver

test: ## Run the test suite
	python src/manage.py test esppa --verbosity=2

shell: ## Open Django shell
	python src/manage.py shell_plus

superuser: ## Create a superuser
	python src/manage.py createsuperuser

seed: ## Import employee CSV data
	python src/manage.py import_employees --clear

collectstatic: ## Collect static files
	python src/manage.py collectstatic --noinput

clean: ## Clean Python cache files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage htmlcov/

check: ## Run Django system checks
	python src/manage.py check --deploy
