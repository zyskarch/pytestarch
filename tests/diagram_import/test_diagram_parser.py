import pytest
from conftest import ROOT_DIR

from pytestarch.diagram_import.diagram_parser import PumlParser
from pytestarch.exceptions import PumlParsingError


def test_error_raised_when_no_puml_start_tag_found() -> None:
    path = ROOT_DIR / "tests/resources/pumls/no_start_tag.puml"
    parser = PumlParser()

    with pytest.raises(
        PumlParsingError,
        match="PUML file needs a start and an end tag.",
    ):
        parser.parse(path)


def test_modules_parsed_correctly_from_puml() -> None:
    path = ROOT_DIR / "tests/resources/pumls/very_simple_example.puml"
    parser = PumlParser()

    parsed_dependencies = parser.parse(path)

    assert parsed_dependencies.all_modules == {"M_A", "M_B"}


def test_dependencies_parsed_correctly_from_puml() -> None:
    path = ROOT_DIR / "tests/resources/pumls/very_simple_example.puml"
    parser = PumlParser()

    parsed_dependencies = parser.parse(path)

    assert parsed_dependencies.dependencies == {"M_A": {"M_B"}}
