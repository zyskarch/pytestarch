from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import pytest

from pytestarch.eval_structure.networkxgraph import NetworkxGraph
from pytestarch.eval_structure.types import Import
from pytestarch.eval_structure_generation.file_import.config import Config
from pytestarch.eval_structure_generation.file_import.converter import ImportConverter
from pytestarch.eval_structure_generation.file_import.file_filter import FileFilter
from pytestarch.eval_structure_generation.file_import.import_types import NamedModule
from pytestarch.eval_structure_generation.file_import.importee_module_calculator import (
    ImporteeModuleCalculator,
)
from pytestarch.eval_structure_generation.file_import.parser import Parser
from pytestarch.utils.partial_match_to_regex_converter import (
    convert_partial_match_to_regex,
)

ROOT_PATH = Path(__file__).parent.parent.parent.resolve()


@pytest.fixture(scope="module")
def modules_and_ast(
    root_path: Path = ROOT_PATH,
    search_path: Path = Path(ROOT_PATH / "tests/resources/importer"),
) -> Tuple[List[str], List[NamedModule]]:
    return Parser(
        FileFilter(
            Config(
                map(
                    lambda s: convert_partial_match_to_regex(s),
                    ("*__pycache__", "*__init__"),
                )
            )
        ),
        root_path,
    ).parse(search_path)


@pytest.fixture(scope="module")
def imports(modules_and_ast: Tuple[List[str], List[NamedModule]]) -> List[Import]:
    return ImportConverter().convert(modules_and_ast[1])


@pytest.fixture(scope="module")
def all_modules(
    modules_and_ast: Tuple[List[str], List[NamedModule]],
    imports: List[Import],
) -> List[str]:
    return ImporteeModuleCalculator(ROOT_PATH).calculate_importee_modules(
        imports,
        modules_and_ast[0],
    )


@pytest.fixture(scope="module")
def module_graph(all_modules: List[str], imports: List[Import]) -> NetworkxGraph:
    return NetworkxGraph(all_modules, imports)


def test_node_edge_count_as_expected(module_graph: NetworkxGraph) -> None:
    assert module_graph.nodes_number == 34
    assert module_graph.edges_number == 30


def test_expected_nodes_present(module_graph: NetworkxGraph) -> None:
    assert "pytestarch.tests.resources.importer" in module_graph
    assert "pytestarch.tests.resources.importer.level0" in module_graph
    assert "pytestarch.tests.resources.importer.level0.level1" in module_graph
    assert "pytestarch.tests.resources.importer.level0.level1.level2" in module_graph
    assert (
        "pytestarch.tests.resources.importer.level0.level1.level2.level3"
        in module_graph
    )
    assert (
        "pytestarch.tests.resources.importer.level0.level1.level2.level3.level4"
        in module_graph
    )
    assert (
        "pytestarch.tests.resources.importer.level0.level1.level2.level3.level4.level5"
        in module_graph
    )
    assert (
        "pytestarch.tests.resources.importer.level0.level1.level2."
        "level3.level4.level5.module_level_5" in module_graph
    )
    assert "pytestarch.tests.resources.importer.level0.test_dummy" in module_graph

    assert "itertools" in module_graph
    assert "pytestarch.tests.resources.importer.level0.test_dummy_2" in module_graph
    assert "pytestarch.tests.resources.importer.level0.test_dummy_3" in module_graph
    assert "os" in module_graph
    assert "io" in module_graph
    assert "typing" in module_graph
    assert "ast" in module_graph
    assert "sys" in module_graph
    assert "pytestarch" in module_graph
    assert "pytestarch.pytestarch" in module_graph
    assert "pytest" in module_graph


def test_edges_between_parent_and_child_modules_as_expected(
    module_graph: NetworkxGraph,
) -> None:
    assert (
        "pytestarch.tests.resources.importer",
        "pytestarch.tests.resources.importer.level0",
    ) in module_graph
    assert (
        "pytestarch.tests.resources.importer.level0",
        "pytestarch.tests.resources.importer.level0.level1",
    ) in module_graph
    assert (
        "pytestarch.tests.resources.importer.level0.level1",
        "pytestarch.tests.resources.importer.level0.level1.level2",
    ) in module_graph
    assert (
        "pytestarch.tests.resources.importer.level0.level1.level2",
        "pytestarch.tests.resources.importer.level0.level1.level2.level3",
    ) in module_graph
    assert (
        "pytestarch.tests.resources.importer.level0.level1.level2.level3",
        "pytestarch.tests.resources.importer.level0.level1.level2.level3.level4",
    ) in module_graph
    assert (
        "pytestarch.tests.resources.importer.level0.level1.level2.level3.level4",
        "pytestarch.tests.resources.importer.level0.level1.level2.level3.level4.level5",
    ) in module_graph
    assert (
        "pytestarch.tests.resources.importer.level0.level1.level2."
        "level3.level4.level5",
        "pytestarch.tests.resources.importer.level0.level1.level2."
        "level3.level4.level5.module_level_5",
    ) in module_graph
    assert (
        "pytestarch.tests.resources.importer.level0",
        "pytestarch.tests.resources.importer.level0.test_dummy",
    ) in module_graph
    assert ("pytestarch", "pytestarch.pytestarch") in module_graph


def test_edges_between_importers_and_importees_as_expected(
    module_graph: NetworkxGraph,
) -> None:
    assert (
        "pytestarch.tests.resources.importer.level0.level1.level2."
        "level3.level4.level5.module_level_5",
        "pytestarch.tests.resources.importer.level0.test_dummy",
    ) in module_graph

    assert (
        "pytestarch.tests.resources.importer.level0.test_dummy",
        "itertools",
    ) in module_graph
    assert (
        "pytestarch.tests.resources.importer.level0.test_dummy",
        "pytestarch.tests.resources.importer.level0.test_dummy_2",
    ) in module_graph
    assert (
        "pytestarch.tests.resources.importer.level0.test_dummy",
        "pytestarch.tests.resources.importer.level0.test_dummy_3",
    ) in module_graph
    assert (
        "pytestarch.tests.resources.importer.level0.test_dummy",
        "ast",
    ) in module_graph
    assert (
        "pytestarch.tests.resources.importer.level0.test_dummy",
        "os",
    ) in module_graph
    assert (
        "pytestarch.tests.resources.importer.level0.test_dummy",
        "io",
    ) in module_graph
    assert (
        "pytestarch.tests.resources.importer.level0.test_dummy",
        "typing",
    ) in module_graph
    assert (
        "pytestarch.tests.resources.importer.level0.test_dummy",
        "sys",
    ) in module_graph
    assert (
        "pytestarch.tests.resources.importer.level0.test_dummy",
        "pytestarch.pytestarch",
    ) in module_graph
    assert (
        "pytestarch.tests.resources.importer.level0.test_dummy",
        "pytest",
    ) in module_graph


def test_graph_connections_as_expected(module_graph: NetworkxGraph) -> None:
    assert (
        "pytestarch.tests.resources.importer.level0.test_dummy",
        "pytest",
    ) in module_graph
    assert ("pytestarch", "pytestarch.pytestarch") in module_graph
