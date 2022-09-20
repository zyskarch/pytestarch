import os

import pytest

from pytestarch.eval_structure.eval_structure_types import Evaluable
from pytestarch.pytestarch import get_evaluable, get_evaluable_for_module_objects
from resources import test_project
from resources.test_project import src


@pytest.fixture(scope="session")
def graph_based_on_string_module_names() -> Evaluable:
    return get_evaluable(
        os.path.dirname(test_project.__file__),
        os.path.dirname(src.__file__),
        ("*__pycache__", "*__init__.py", "*Test.py"),
    )


@pytest.fixture(scope="session")
def graph_based_on_module_objects() -> Evaluable:
    return get_evaluable_for_module_objects(
        test_project,
        src,
        ("*__pycache__", "*__init__.py", "*Test.py"),
    )


@pytest.fixture(scope="session")
def graph_with_identical_source_and_module_path() -> Evaluable:
    return get_evaluable_for_module_objects(
        src,
        src,
        ("*__pycache__", "*__init__.py", "*Test.py"),
    )


@pytest.fixture(scope="session")
def graph_with_level_limit_1() -> Evaluable:
    return get_evaluable(
        os.path.dirname(test_project.__file__),
        os.path.dirname(src.__file__),
        ("*__pycache__", "*__init__.py", "*Test.py"),
        level_limit=1,
    )


@pytest.fixture(scope="session")
def graph_including_tests() -> Evaluable:
    return get_evaluable(
        os.path.dirname(test_project.__file__),
        os.path.dirname(src.__file__),
        ("*__pycache__", "*__init__.py"),
    )
