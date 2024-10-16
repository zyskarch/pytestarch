from __future__ import annotations

from pathlib import Path

import pytest

from pytestarch import EvaluableArchitecture, Rule, get_evaluable_architecture


@pytest.fixture(scope="session")
def pytestarch_architecture() -> EvaluableArchitecture:
    """Running the test in isolation leads to a different cwd than when running via the full pytest suite. Therefore,
    walk up in the file hierarchy until the top level folder is reached."""
    cwd = Path.cwd()
    while cwd.stem != "pytestarch":
        cwd = cwd.parent
    src_folder = str(cwd / "src/pytestarch")

    return get_evaluable_architecture(
        src_folder,
        src_folder,
        ("*__pycache__", "*__init__.py"),
    )


BASE_MODULE = "pytestarch"
DIAGRAM = f"{BASE_MODULE}.diagram_extension"
STRUCTURE = f"{BASE_MODULE}.eval_structure"
GENERATION = f"{BASE_MODULE}.eval_structure_generation"
LANGUAGE = f"{BASE_MODULE}.query_language"
ASSESSMENT = f"{BASE_MODULE}.rule_assessment"
UTILS = f"{BASE_MODULE}.utils"


top_level_rules = [
    pytest.param(
        Rule()
        .modules_that()
        .are_named(DIAGRAM)
        .should_only()
        .import_modules_that()
        .are_named(LANGUAGE),
        id="diagram_extension",
        marks=pytest.mark.skip,
    ),
    pytest.param(
        Rule().modules_that().are_named(STRUCTURE).should_not().import_anything(),
        id="eval_structure",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(GENERATION)
        .should_only()
        .import_modules_that()
        .are_named(STRUCTURE),
        id="eval_structure_generation",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(LANGUAGE)
        .should_only()
        .import_modules_that()
        .are_named([STRUCTURE, ASSESSMENT, UTILS]),
        id="query_language",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(ASSESSMENT)
        .should_only()
        .import_modules_that()
        .are_named(STRUCTURE),
        id="rule_assessment",
    ),
]


@pytest.mark.parametrize("rule", top_level_rules)
def test_top_level_module_structure(
    rule: Rule, pytestarch_architecture: EvaluableArchitecture
) -> None:
    rule.assert_applies(pytestarch_architecture)
