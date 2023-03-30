check-linting:
	vulture src/ --min-confidence 70 --exclude src/diator/container.py
	isort --check --profile black src/ tests/
	flake8 src/ tests/ --exit-zero
	black --diff --check src/ tests/
	mypy src/ --pretty


fix-linting:
	isort --profile black src/ tests/
	black --diff src/ tests/


artifacts: test
	python -m build


clean:
	rm -rf dist/


prepforbuild:
	pip install build


build:
	python -m build


test-release:
	twine upload --repository testpypi dist/* --verbose


release:
	twine upload --repository pypi dist/* --verbose


test:
	pytest
