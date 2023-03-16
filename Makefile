lint:
	flake8 src/ tests/ --exit-zero
	black --check src/ tests/
	vulture src/ --min-confidence 70 --exclude src/diator/container.py
	mypy src/ tests/ --pretty


artifacts: test
	python -m build


clean:
	rm -rf dist/


prepforbuild:
	pip install build


build:
	python -m build


test-release:
	twine upload --repository testpypi dist/*


release:
	twine upload --repository pypi dist/*


test:
	pytest
