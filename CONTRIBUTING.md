# Contributing

This page discribes how to contribute to Diator.

## Requirements

- supported Python version (e.g. Python 3.10 or Python 3.11).
- Linux, since all development proccess adapted for Linux machines.

## Environment preparation

1. fork the [repository](https://github.com/akhundMurad/diator)
2. clone the forked repository
3. create a Python virtual environment in the desired location:

    ```bash
    python -m venv .venv
    ```

4. activate environment:

    ```bash
    source .venv/bin/activate
    ```

5. install dev dependencies:

    ```bash
    pip install -e .["test"]
    ```

6. run tests:

    ```bash
    make test
    ```

## Formatters

We are using the following linters:

- black
- flake8
- vulture
- mypy
- isort

`Makefile` supports a task to run linters:

```bash
make check-linting
```

## How to name branches

It doesn't matter, as long as branch names don't contain anything that violates the Code of Conduct included in the project's repository. As a general rule of thumb, branch names should have a descriptive name, or refer the number of an issue in their name.
