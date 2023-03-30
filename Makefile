check-linting:
	vulture src/ --min-confidence 70 --exclude src/diator/container.py
	isort --check --profile black src/ tests/ examples/
	flake8 --exit-zero src/ tests/ examples/
	black --check --diff src/ tests/ examples/
	mypy src/ --pretty


fix-linting:
	isort --profile black src/ tests/ examples/
	black src/ tests/ examples/


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
