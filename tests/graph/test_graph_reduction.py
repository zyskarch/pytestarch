import pytest

import resources
from pytestarch.eval_structure.eval_structure_types import Evaluable
from pytestarch.pytestarch import get_evaluable_for_module_objects
from resources import importer


@pytest.fixture(scope="session")
def simple_graph_level_1() -> Evaluable:
    return get_evaluable_for_module_objects(
        resources,
        importer,
        ("*__pycache__", "*__init__.py"),
        level_limit=1,
        exclude_external_libraries=False,
    )


def test_nodes_as_expected(simple_graph_level_1: Evaluable) -> None:
    graph = simple_graph_level_1._graph

    assert "importer" in graph
    assert "importer.sub_dir" in graph
    assert "importer.level0" in graph
    assert "importer.level0.level1" not in graph

    assert "itertools" in graph
    assert "os" in graph
    assert "io" in graph
    assert "typing" in graph
    assert "ast" in graph
    assert "sys" in graph
    assert "pytestarch" in graph
    assert "pytestarch.pytestarch" in graph
    assert "pytest" in graph


def test_edges_between_parent_and_child_modules_as_expected(
    simple_graph_level_1: Evaluable,
) -> None:
    graph = simple_graph_level_1._graph
    assert ("importer", "importer.level0") in graph


def test_edges_between_importers_and_importees_as_expected(
    simple_graph_level_1: Evaluable,
) -> None:
    graph = simple_graph_level_1._graph
    assert ("importer.level0", "itertools") in graph
    assert ("importer.level0", "ast") in graph
    assert ("importer.level0", "os") in graph
    assert ("importer.level0", "io") in graph
    assert ("importer.level0", "typing") in graph
    assert ("importer.level0", "sys") in graph
    assert ("importer.level0", "pytestarch.pytestarch") in graph
    assert ("importer.level0", "pytest") in graph
