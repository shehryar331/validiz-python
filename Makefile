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

