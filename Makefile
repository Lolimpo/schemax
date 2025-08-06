PROJECT_NAME=schemax

.PHONY: install
install:
	uv sync --group dev

.PHONY: test
test:
	uv run python -m pytest

.PHONY: lint
lint:
	uv run mypy ${PROJECT_NAME} --strict
	uv run ruff check --fix ${PROJECT_NAME} tests

.PHONY: all
all: install lint test

.PHONY: clean
clean:
	rm -rf dist/ build/ *.egg-info/

.PHONY: test-in-docker
test-in-docker:
	docker run -v `pwd`:/tmp/app -w /tmp/app python:$(or $(PYTHON_VERSION),3.13) sh -c "pip install uv && uv sync && uv run python -m pytest"

.PHONY: all-in-docker
all-in-docker:
	docker run -v `pwd`:/tmp/app -w /tmp/app python:$(or $(PYTHON_VERSION),3.13) sh -c "pip install uv && make all"
