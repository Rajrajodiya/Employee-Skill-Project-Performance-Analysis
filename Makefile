# ═════════════════════════════════════════════════════════════════════════════
#  ESPPA - Makefile
#  Common commands for development and deployment.
# ═════════════════════════════════════════════════════════════════════════════

.PHONY: help install migrate run test shell superuser clean docker-build docker-up

help: ## Display this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	pip install -r requirements.txt

migrate: ## Run database migrations
	python src/manage.py migrate

makemigrations: ## Create new migrations
	python src/manage.py makemigrations

run: ## Run development server
	python src/manage.py runserver

test: ## Run the test suite
	python src/manage.py test esppa --verbosity=2

test-coverage: ## Run tests with coverage report
	pip install coverage && coverage run src/manage.py test esppa && coverage report -m

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

docker-build: ## Build Docker image
	docker compose build

docker-up: ## Start Docker containers
	docker compose up -d

docker-down: ## Stop Docker containers
	docker compose down

check: ## Run Django system checks
	python src/manage.py check --deploy

# ═════════════════════════════════════════════════════════════════════════════
#  DVC (Data Version Control)
# ═════════════════════════════════════════════════════════════════════════════

dvc-init: ## Initialize DVC (run once per project)
	dvc init

dvc-track: ## Track dataset and models with DVC
	dvc add static/employee_data.csv
	dvc add src/apps/esppa/models/

dvc-push: ## Push data to DVC remote
	dvc push

dvc-pull: ## Pull data from DVC remote
	dvc pull

dvc-status: ## Check DVC status
	dvc status

# ═════════════════════════════════════════════════════════════════════════════
#  Vercel Deployment
# ═════════════════════════════════════════════════════════════════════════════

vercel-dev: ## Run Vercel development server locally
	vercel dev

vercel-deploy: ## Deploy to Vercel production
	vercel --prod

vercel-deploy-preview: ## Deploy preview to Vercel
	vercel
