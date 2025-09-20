.PHONY: help install dev-install run test lint format clean docker-build docker-run migrate

help:
	@echo "Available commands:"
	@echo "  install      - Install production dependencies"
	@echo "  dev-install  - Install development dependencies"
	@echo "  run          - Run the FastAPI server"
	@echo "  test         - Run tests"
	@echo "  lint         - Run linting (mypy)"
	@echo "  format       - Format code (black + isort)"
	@echo "  clean        - Clean cache and build files"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run with Docker Compose"
	@echo "  migrate      - Run database migrations"

install:
	pip install -r requirements.txt

dev-install:
	pip install -r requirements.txt
	pip install pytest pytest-asyncio pytest-mock black isort mypy

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest

lint:
	mypy app/

format:
	black app/
	isort app/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

docker-build:
	docker build -t delegate-ai-backend .

docker-run:
	docker-compose up --build

migrate:
	alembic upgrade head

celery-worker:
	celery -A app.background_jobs.worker worker --loglevel=info

celery-beat:
	celery -A app.background_jobs.worker beat --loglevel=info

dev-setup: dev-install
	cp .env.example .env
	@echo "Please edit .env with your configuration"