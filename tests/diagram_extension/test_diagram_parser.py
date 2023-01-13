from __future__ import annotations

import pytest
from conftest import ROOT_DIR

from pytestarch.diagram_extension.diagram_parser import PumlParser
from pytestarch.diagram_extension.exceptions import PumlParsingError


def test_error_raised_when_no_puml_start_tag_found() -> None:
    path = ROOT_DIR / "tests/resources/pumls/no_start_tag.puml"
    parser = PumlParser()

    with pytest.raises(
        PumlParsingError,
        match="No diagram specification found",
    ):
        parser.parse(path)


def test_modules_parsed_correctly_from_puml() -> None:
    path = ROOT_DIR / "tests/resources/pumls/very_simple_example.puml"
    parser = PumlParser()

    parsed_dependencies = parser.parse(path)

    assert parsed_dependencies.all_modules == {"M_A", "M_B", "M_C"}


def test_all_module_types_parsed_correctly_from_puml() -> None:
    path = ROOT_DIR / "tests/resources/pumls/all_component_declaration_types.puml"
    parser = PumlParser()

    parsed_dependencies = parser.parse(path)

    assert parsed_dependencies.all_modules == {"M_A", "M_B", "M_C", "M_D", "M_E"}


def test_module_aliases_resolved_correctly() -> None:
    path = ROOT_DIR / "tests/resources/pumls/all_component_declaration_types.puml"
    parser = PumlParser()

    parsed_dependencies = parser.parse(path)

    assert parsed_dependencies.dependencies["M_A"] == {"M_C"}


def test_all_module_and_dependency_types_parsed_correctly_from_puml() -> None:
    path = ROOT_DIR / "tests/resources/pumls/all_dependency_declaration_types.puml"
    parser = PumlParser()

    parsed_dependencies = parser.parse(path)

    assert parsed_dependencies.all_modules == {"M_A", "M_B", "M_C", "M_D", "M_E", "M_F"}
    assert parsed_dependencies.dependencies == {
        "M_A": {"M_B"},
        "M_B": {"M_A"},
        "M_C": {"M_D"},
        "M_D": {"M_C"},
        "M_E": {"M_F"},
        "M_F": {"M_E"},
    }


def test_dependencies_parsed_correctly_from_puml() -> None:
    path = ROOT_DIR / "tests/resources/pumls/very_simple_example.puml"
    parser = PumlParser()

    parsed_dependencies = parser.parse(path)

    assert parsed_dependencies.dependencies == {"M_C": {"M_B"}, "M_B": {"M_C"}}


def test_diagram_with_multiple_components_file() -> None:
    path = (
        ROOT_DIR / "tests/resources/pumls/multiple_component_example_with_brackets.puml"
    )
    parser = PumlParser()

    parsed_dependencies = parser.parse(path)

    expected_modules = {
        "exporter",
        "importer",
        "logging_util",
        "model",
        "orchestration",
        "persistence",
        "runtime",
        "services",
        "simulation",
        "util",
    }
    expected_dependencies = {
        "runtime": {"persistence", "orchestration", "services", "logging_util", "util"},
        "services": {"persistence", "model", "util", "importer"},
        "orchestration": {
            "exporter",
            "simulation",
            "model",
            "logging_util",
            "util",
            "importer",
        },
        "importer": {"model", "util"},
        "logging_util": {"util"},
        "simulation": {"model", "util", "logging_util"},
        "persistence": {"model", "util"},
        "exporter": {"model", "util", "logging_util"},
    }

    assert parsed_dependencies.all_modules == expected_modules
    assert parsed_dependencies.dependencies == expected_dependencies
