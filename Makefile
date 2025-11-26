.PHONY: help install test lint format clean dev docker-build docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies with uv"
	@echo "  make test          - Run all tests"
	@echo "  make test-unit     - Run unit tests only"
	@echo "  make test-int      - Run integration tests only"
	@echo "  make lint          - Run linting checks"
	@echo "  make format        - Format code with ruff"
	@echo "  make typecheck     - Run mypy type checking"
	@echo "  make clean         - Clean cache and build files"
	@echo "  make dev           - Run development server"
	@echo "  make docker-build  - Build Docker images"
	@echo "  make docker-up     - Start Docker services"
	@echo "  make docker-down   - Stop Docker services"

install:
	uv sync --all-extras
	uv run pre-commit install

test:
	uv run pytest

test-unit:
	uv run pytest -m unit

test-int:
	uv run pytest -m integration

test-cov:
	uv run pytest --cov=src --cov-report=html --cov-report=term

lint:
	uv run ruff check .
	uv run mypy src

format:
	uv run ruff format .
	uv run ruff check --fix .

typecheck:
	uv run mypy src

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	rm -f .coverage

dev:
	uv run uvicorn src.api.main:app --reload --port 8000

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

pre-commit:
	uv run pre-commit run --all-files
