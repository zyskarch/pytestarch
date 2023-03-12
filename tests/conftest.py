from __future__ import annotations

import os
from pathlib import Path

import pytest

from pytestarch import EvaluableArchitecture
from pytestarch.pytestarch import (
    get_evaluable_architecture,
    get_evaluable_architecture_for_module_objects,
)
from resources import flat_test_project_1, flat_test_project_2
from resources.test_project import src

ROOT_DIR = Path(__file__).parent.parent.resolve()


@pytest.fixture(scope="session")
def graph_based_on_string_module_names() -> EvaluableArchitecture:
    return get_evaluable_architecture(
        os.path.dirname(src.__file__),
        os.path.dirname(src.__file__),
        ("*__pycache__", "*__init__.py", "*Test.py"),
    )


@pytest.fixture(scope="session")
def graph_based_on_module_objects() -> EvaluableArchitecture:
    return get_evaluable_architecture_for_module_objects(
        src,
        src,
        ("*__pycache__", "*__init__.py", "*Test.py"),
    )


@pytest.fixture(scope="session")
def graph_with_identical_source_and_module_path() -> EvaluableArchitecture:
    return get_evaluable_architecture_for_module_objects(
        src,
        src,
        ("*__pycache__", "*__init__.py", "*Test.py"),
    )


@pytest.fixture(scope="session")
def graph_with_level_limit_1() -> EvaluableArchitecture:
    return get_evaluable_architecture(
        os.path.dirname(src.__file__),
        os.path.dirname(src.__file__),
        ("*__pycache__", "*__init__.py", "*Test.py"),
        level_limit=1,
    )


@pytest.fixture(scope="session")
def graph_including_tests() -> EvaluableArchitecture:
    return get_evaluable_architecture(
        os.path.dirname(src.__file__),
        os.path.dirname(src.__file__),
        ("*__pycache__", "*__init__.py"),
    )


@pytest.fixture(scope="module")
def flat_project_1() -> EvaluableArchitecture:
    return get_evaluable_architecture(
        os.path.dirname(flat_test_project_1.__file__),
        os.path.dirname(flat_test_project_1.__file__),
        ("*__pycache__", "*__init__.py", "*Test.py"),
    )


@pytest.fixture(scope="module")
def flat_project_2() -> EvaluableArchitecture:
    return get_evaluable_architecture(
        os.path.dirname(flat_test_project_2.__file__),
        os.path.dirname(flat_test_project_2.__file__),
        ("*__pycache__", "*__init__.py", "*Test.py"),
    )
