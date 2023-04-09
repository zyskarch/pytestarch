from __future__ import annotations

from typing import List

import pytest
from eval_structure.evaluable_graph.conftest import MODULE_A, MODULE_B, MODULE_D
from integration.interesting_rules_for_tests import A, B, C

from pytestarch import Rule
from pytestarch.eval_structure.evaluable_architecture import (
    EvaluableArchitecture,
    Module,
)
from pytestarch.eval_structure.evaluable_graph import EvaluableArchitectureGraph
from pytestarch.eval_structure.exceptions import ImpossibleMatch
from pytestarch.eval_structure.module_name_converter import ModuleNameConverter
from pytestarch.utils.partial_match_to_regex_converter import (
    convert_partial_match_to_regex,
)

MODULE = "test.module.submodule.class"


partial_match_test_cases = [
    pytest.param(
        "test.module.submodule.class", True, id="complete match - match_regex"
    ),
    pytest.param(
        "test.module.submodule.clasz", False, id="complete match - no match_regex"
    ),
    pytest.param(".*\\.class", True, id="end match - match_regex"),
    pytest.param(".*\\.clasz", False, id="end match - no match_regex"),
    pytest.param("test\\..*", True, id="start match - match_regex"),
    pytest.param("test,.*", False, id="start match - no match_regex"),
    pytest.param(".*le\\.submo.*", True, id="inner match - match_regex"),
    pytest.param("les\\.submo.*", False, id="inner match - no match_regex"),
]


@pytest.mark.parametrize("match, expected_result", partial_match_test_cases)
def test_partial_match(match: str, expected_result: bool) -> None:
    assert ModuleNameConverter._name_matches_pattern(match, MODULE) == expected_result


@pytest.mark.parametrize(
    "module_matches",
    [
        [
            Module(name=convert_partial_match_to_regex("*D"), regex=True),
            Module(name=convert_partial_match_to_regex("*A*"), regex=True),
        ],
        [
            Module(name=".*D", regex=True),
            Module(name=".*A.*", regex=True),
        ],
    ],
)
def test_module_matches(
    module_matches: List[Module], submodule_evaluable: EvaluableArchitectureGraph
) -> None:
    calculated_matches, conversion_mapping = ModuleNameConverter.convert(
        module_matches, submodule_evaluable
    )

    assert len(calculated_matches) == 3

    module_a = Module(name=MODULE_A)
    module_b = Module(name=MODULE_B)
    module_d = Module(name=MODULE_D)

    assert module_a in calculated_matches
    assert module_b in calculated_matches
    assert module_d in calculated_matches

    assert len(conversion_mapping.keys()) == 2

    assert conversion_mapping[module_matches[0].name] == [module_d]
    assert conversion_mapping[module_matches[1].name] == [module_a, module_b, module_d]


def test_never_matched_match_raises_error(
    evaluable: EvaluableArchitectureGraph,
) -> None:
    module_matches = [Module(name="I will not match", regex=True)]
    with pytest.raises(
        ImpossibleMatch, match="No modules found that match: I will not match"
    ):
        ModuleNameConverter.convert(module_matches, evaluable)


test_cases = [
    pytest.param(
        # src.moduleC and src.moduleA
        Rule()
        .modules_that()
        .have_name_matching(".*moduleC$")
        .should()
        .import_modules_that()
        .have_name_matching(".*moduleA$"),
        f'"{C}" does not import "{A}".',
        id="regex_single_match",
    ),
    pytest.param(
        # src.moduleC and src.moduleA
        Rule()
        .modules_that()
        .have_name_containing("*moduleC")
        .should()
        .import_modules_that()
        .have_name_containing("*moduleA"),
        f'"{C}" does not import "{A}".',
        id="partial_match_single_match",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should()
        .import_modules_that()
        .have_name_matching("src\\.module[AB]$"),
        f'"{C}" does not import "{A}", "{B}".',
        id="regex_two_matches",
    ),
]


@pytest.mark.parametrize("rule, expected_error_message", test_cases)
def test_regex_module_match_as_expected(
    rule: Rule,
    expected_error_message: str,
    graph_based_on_string_module_names: EvaluableArchitecture,
) -> None:
    with pytest.raises(AssertionError, match=expected_error_message):
        rule.assert_applies(graph_based_on_string_module_names)
