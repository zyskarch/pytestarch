import pytest

from conftest import ROOT_DIR
from pytestarch import DiagramRule, EvaluableArchitecture
from pytestarch.diagram_import.parsed_dependencies import ParsedDependencies
from pytestarch.eval_structure.evaluable_graph import EvaluableArchitectureGraph
from pytestarch.eval_structure_impl.networkxgraph import NetworkxGraph
from pytestarch.importer.import_types import AbsoluteImport
from pytestarch.query_language.diagrams.diagram_rule import ModulePrefixer

MODULE_1 = "M_A"
MODULE_2 = "M_B"


@pytest.fixture(scope="module")
def evaluable() -> EvaluableArchitecture:
    all_modules = [MODULE_1, MODULE_2]
    imports = [
        AbsoluteImport(MODULE_1, MODULE_2),
    ]

    return EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))


@pytest.fixture(scope="module")
def evaluable2() -> EvaluableArchitecture:
    all_modules = [MODULE_1, MODULE_2]
    imports = [
        AbsoluteImport(MODULE_2, MODULE_1),
    ]

    return EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))


def test_puml_diagram_integration_rules_fulfilled(
    evaluable: EvaluableArchitecture,
) -> None:
    path = ROOT_DIR / "tests/resources/pumls/very_simple_example.puml"

    rule = DiagramRule().from_file(path).base_module_included_in_module_names()

    rule.assert_applies(evaluable)


def test_puml_diagram_integration_rules_violated(
    evaluable2: EvaluableArchitecture,
) -> None:
    path = ROOT_DIR / "tests/resources/pumls/very_simple_example.puml"

    rule = DiagramRule().from_file(path).base_module_included_in_module_names()

    with pytest.raises(AssertionError, match='"M_B" imports "M_A".'):
        rule.assert_applies(evaluable2)


# TODO: integration test with actual code (with base module and and without)
# TODO should only or should not configurable
# TODO: high level documentation


def test_base_module_names_prefixed() -> None:
    dependencies = ParsedDependencies(
        {MODULE_1, MODULE_2}, {MODULE_1: {MODULE_1, MODULE_2}}
    )

    prefix = "I am a prefix"

    prefixed = ModulePrefixer(prefix).prefix(dependencies)

    module_1_prefixed = f"{prefix}.{MODULE_1}"
    module_2_prefixed = f"{prefix}.{MODULE_2}"

    assert prefixed.all_modules == {module_1_prefixed, module_2_prefixed}
    assert prefixed.dependencies == {
        module_1_prefixed: {module_1_prefixed, module_2_prefixed}
    }
