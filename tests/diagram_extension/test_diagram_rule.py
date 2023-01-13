from __future__ import annotations

import os

import pytest
from conftest import ROOT_DIR
from resources import flat_test_project_1, flat_test_project_2

from pytestarch import DiagramRule, EvaluableArchitecture, get_evaluable_architecture
from pytestarch.diagram_extension.diagram_rule import ModulePrefixer
from pytestarch.diagram_extension.parsed_dependencies import ParsedDependencies
from pytestarch.eval_structure.evaluable_graph import EvaluableArchitectureGraph
from pytestarch.eval_structure.networkxgraph import NetworkxGraph
from pytestarch.eval_structure_generation.file_import.import_types import AbsoluteImport

MULTIPLE_COMPONENTS_FILE_PATH = (
    ROOT_DIR / "tests/resources/pumls/multiple_component_example_with_brackets.puml"
)
SINGLE_IMPORT_AND_ISOLATED_COMPONENT_FILE_PATH = (
    ROOT_DIR / "tests/resources/pumls/very_simple_example.puml"
)


MODULE_1 = "M_A"
MODULE_2 = "M_B"
MODULE_3 = "M_C"


@pytest.fixture(scope="module")
def evaluable() -> EvaluableArchitecture:
    all_modules = [MODULE_1, MODULE_2, MODULE_3]
    imports = [
        AbsoluteImport(MODULE_3, MODULE_2),
        AbsoluteImport(MODULE_2, MODULE_3),
    ]

    return EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))


@pytest.fixture(scope="module")
def evaluable2() -> EvaluableArchitecture:
    all_modules = [MODULE_1, MODULE_2, MODULE_3]
    imports = [
        AbsoluteImport(MODULE_2, MODULE_1),
        AbsoluteImport(MODULE_2, MODULE_3),
    ]

    return EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))


@pytest.fixture(scope="module")
def evaluable3() -> EvaluableArchitecture:
    all_modules = [MODULE_1, MODULE_2, MODULE_3]
    imports = [
        AbsoluteImport(MODULE_3, MODULE_2),
        AbsoluteImport(MODULE_1, MODULE_2),
    ]

    return EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))


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


def test_puml_diagram_integration_rules_fulfilled(
    evaluable: EvaluableArchitecture,
) -> None:
    path = SINGLE_IMPORT_AND_ISOLATED_COMPONENT_FILE_PATH

    rule = DiagramRule().from_file(path).base_module_included_in_module_names()

    rule.assert_applies(evaluable)


def test_puml_diagram_integration_rules_violated(
    evaluable2: EvaluableArchitecture,
) -> None:
    path = SINGLE_IMPORT_AND_ISOLATED_COMPONENT_FILE_PATH

    rule = DiagramRule().from_file(path).base_module_included_in_module_names()

    with pytest.raises(AssertionError, match='"M_B" imports "M_A".'):
        rule.assert_applies(evaluable2)


def test_isolated_component_included_in_should_not_rules_violated(
    evaluable3: EvaluableArchitecture,
) -> None:
    path = SINGLE_IMPORT_AND_ISOLATED_COMPONENT_FILE_PATH

    rule = DiagramRule().from_file(path).base_module_included_in_module_names()

    with pytest.raises(AssertionError, match='"M_A" imports "M_B"'):
        rule.assert_applies(evaluable3)


def test_puml_diagram_integration_multiple_components_rules_fulfilled(
    flat_project_1: EvaluableArchitecture,
) -> None:
    path = MULTIPLE_COMPONENTS_FILE_PATH

    rule = DiagramRule().from_file(path).with_base_module("flat_test_project_1")

    rule.assert_applies(flat_project_1)


def test_puml_diagram_integration_multiple_components_rules_violated(
    flat_project_2: EvaluableArchitecture,
) -> None:
    path = MULTIPLE_COMPONENTS_FILE_PATH

    rule = DiagramRule().from_file(path).with_base_module("flat_test_project_2")

    with pytest.raises(
        AssertionError, match='"flat_test_project_2.exporter" does not import'
    ):
        rule.assert_applies(flat_project_2)


def test_base_module_names_prefixed() -> None:
    dependencies = ParsedDependencies(
        {MODULE_1, MODULE_2}, {MODULE_1: {MODULE_1, MODULE_2}}
    )

    prefix = "I am a prefix"

    prefixed = ModulePrefixer.prefix(dependencies, prefix)

    module_1_prefixed = f"{prefix}.{MODULE_1}"
    module_2_prefixed = f"{prefix}.{MODULE_2}"

    assert prefixed.all_modules == {module_1_prefixed, module_2_prefixed}
    assert prefixed.dependencies == {
        module_1_prefixed: {module_1_prefixed, module_2_prefixed}
    }
