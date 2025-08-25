.PHONY: install install-dev test lint format type-check clean run-cli docker-build docker-up

# Install dependencies
install:
	uv sync

install-dev:
	uv sync --dev

# Testing
test:
	uv run pytest

test-fast:
	uv run pytest -n auto --dist loadgroup

test-parallel:
	uv run pytest -n 8 --dist loadscope

test-unit:
	uv run pytest tests/unit -n auto

test-integration:
	uv run pytest tests/integration -n 2

test-performance:
	uv run pytest tests/performance -n 1 --benchmark-only

test-cov:
	uv run pytest --cov=scrap_e --cov-report=html --cov-report=term

test-watch:
	uv run pytest-watch -- -n auto

# Code quality
lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/

type-check:
	uv run mypy src/

actionlint:
	@echo "Checking GitHub Actions workflows..."
	@if command -v actionlint >/dev/null 2>&1; then \
		actionlint .github/workflows/*.yml; \
	elif command -v docker >/dev/null 2>&1; then \
		docker run --rm -v $$(pwd):/repo --workdir /repo rhysd/actionlint:latest -color; \
	else \
		echo "Installing actionlint..."; \
		curl -s https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash | bash; \
		./actionlint .github/workflows/*.yml; \
	fi

check-all: lint format type-check actionlint
	@echo "All checks passed!"

# Clean
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .ruff_cache .mypy_cache
	rm -rf htmlcov .coverage

# Run
run-cli:
	uv run scrap-e --help

doctor:
	uv run scrap-e doctor

# Docker
docker-build:
	docker build -t scrap-e .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

# Development
dev-server:
	uv run scrap-e serve

# Examples
example-http:
	uv run python examples/basic_usage.py

example-scrape:
	uv run scrap-e scrape https://example.com -o output.json
