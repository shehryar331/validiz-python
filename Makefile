.PHONY: sort
sort: 
	isort .

.PHONY: format
format: 
	uv run ruff format

.PHONY: lint
lint:
	uv run ruff check

.PHONY: mypy
mypy: 
	uv run mypy . --check-untyped-defs

.PHONY: qa
qa: sort format lint

.PHONY: test
test:
	uv run pytest

.PHONY: test-coverage
test-coverage:
	uv run pytest --cov=validiz --cov-report=term-missing