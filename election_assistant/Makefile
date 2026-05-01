.PHONY: test lint format

test:
	pytest tests/ --cov=. --cov-report=term-missing -v

lint:
	flake8 . --max-line-length=88
	black --check .

format:
	black .
