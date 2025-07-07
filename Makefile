.PHONY: help test test-unit test-integration test-e2e test-debug clean lint format install dev-install run

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install:  ## Install production dependencies
	pip install -r requirements.txt

dev-install:  ## Install development dependencies
	pip install -r requirements.txt
	pip install pytest pytest-cov black flake8 mypy

test:  ## Run all tests
	pytest test/

test-unit:  ## Run unit tests only
	pytest test/unit/

test-integration:  ## Run integration tests only
	pytest test/integration/

test-e2e:  ## Run end-to-end tests only
	pytest test/e2e/

test-debug:  ## Run debug tests only
	pytest test/debug/

test-coverage:  ## Run tests with coverage report
	pytest test/ --cov=src --cov-report=html --cov-report=term

lint:  ## Run linting checks
	flake8 src/
	mypy src/

format:  ## Format code with black
	black src/ test/

clean:  ## Clean up generated files
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:  ## Run the application
	python main.py

dev:  ## Run the application in development mode
	python main.py --debug

deploy:  ## Deploy the application (run deployment script)
	./src/scripts/deploy.sh
