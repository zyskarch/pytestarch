# Development Guide

If you want to help develop PyTestArch, please read the following guide on setting up the development environment 
and on which requirements need to be fulfilled for a PR to be ready for approval.

## Setting up
[Poetry](https://python-poetry.org/) is used for dependency and packaging management. Install poetry if you haven't already.
Run `poetry install` to create a virtual environment with the required dependencies.

There are also git hooks for black, flake8, isort, and bandit available via `pre-commit install`.

## Running the test suite
To make sure that everything works as expected, run `nox`.


## Requirements for PRs
When opening a PR, make sure the following requirements are fulfilled:
1. All existing tests should pass: Run `nox` to ensure this.
2. Ensure your code is properly formatted. Make sure you are using the pre-commit hooks to ensure this.
3. For new features or bugfixes, your added code should be covered by new tests.
4. Add your changes to the [changelog](docs/changelog.md).
5. Update existing doc strings and documentation.
6. Add doc strings for newly added public functions and methods.
7. Add doc strings for complicated "private" functions and methods.
8. Add high level documentation for new features.
