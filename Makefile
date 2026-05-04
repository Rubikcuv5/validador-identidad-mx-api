.PHONY: test

test:
	pytest -v --cov=app --cov-fail-under=80
