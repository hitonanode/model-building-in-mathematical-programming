.PHONY: all
all: check-format check-lint check-type

.PHONY: check-format
check-format:
	@poetry run ruff format --check src/

.PHONY: fix-format
fix-format:
	@poetry run ruff format src/

.PHONY: check-lint
check-lint:
	@poetry run ruff check src/

.PHONY: fix-lint
fix-lint:
	@poetry run ruff check --fix src/

.PHONY: check-type
check-type:
	@poetry run mypy --strict --enable-incomplete-feature=NewGenericSyntax src/
