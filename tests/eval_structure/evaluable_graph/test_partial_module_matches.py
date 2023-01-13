from __future__ import annotations

import pytest
from eval_structure.evaluable_graph.conftest import MODULE_A, MODULE_B, MODULE_D

from pytestarch.eval_structure.evaluable_architecture import Module
from pytestarch.eval_structure.evaluable_graph import EvaluableArchitectureGraph
from pytestarch.eval_structure.exceptions import ImpossibleMatch

MODULE = "test.module.submodule.class"


partial_match_test_cases = [
    pytest.param("test.module.submodule.class", True, id="complete match - match"),
    pytest.param("test.module.submodule.clasz", False, id="complete match - no match"),
    pytest.param("*.class", True, id="end match - match"),
    pytest.param("*.clasz", False, id="end match - no match"),
    pytest.param("test.*", True, id="start match - match"),
    pytest.param("test,*", False, id="start match - no match"),
    pytest.param("*le.submo*", True, id="inner match - match"),
    pytest.param("les.submo*", False, id="inner match - no match"),
]


@pytest.mark.parametrize("match, expected_result", partial_match_test_cases)
def test_partial_match(match: str, expected_result: bool) -> None:
    assert (
        EvaluableArchitectureGraph._partial_name_match(match, MODULE) == expected_result
    )


def test_module_matches(submodule_evaluable: EvaluableArchitectureGraph) -> None:
    module_matches = [
        Module(name="*D", partial_match=True),
        Module(name="*A*", partial_match=True),
    ]

    calculated_matches = submodule_evaluable._convert_to_full_name_matches(
        [module_matches]
    )

    assert len(calculated_matches) == 1
    assert len(calculated_matches[0]) == 3

    assert Module(name=MODULE_A) in calculated_matches[0]
    assert Module(name=MODULE_B) in calculated_matches[0]
    assert Module(name=MODULE_D) in calculated_matches[0]


def test_non_partial_module_does_not_match_anything_but_itself(
    submodule_evaluable: EvaluableArchitectureGraph,
) -> None:
    module_matches = [Module(name="*.*")]

    calculated_matches = submodule_evaluable._convert_to_full_name_matches(
        [module_matches]
    )

    assert len(calculated_matches) == 1
    assert len(calculated_matches[0]) == 1

    assert Module(name="*.*") in calculated_matches[0]


def test_never_matched_match_raises_error(
    evaluable: EvaluableArchitectureGraph,
) -> None:
    module_matches = [Module(name="I will not match", partial_match=True)]

    with pytest.raises(
        ImpossibleMatch, match="No modules found that match: I will not match"
    ):
        evaluable._convert_to_full_name_matches([module_matches])


def test_module_matches_reported_separately_by_group(
    submodule_evaluable: EvaluableArchitectureGraph,
) -> None:
    module_matches_1 = [
        Module(name="*D", partial_match=True),
    ]

    module_matches_2 = [
        Module(name="*A*", partial_match=True),
    ]

    calculated_matches = submodule_evaluable._convert_to_full_name_matches(
        [module_matches_1, module_matches_2]
    )

    assert len(calculated_matches) == 2

    assert len(calculated_matches[0]) == 1
    assert len(calculated_matches[1]) == 3

    assert Module(name=MODULE_D) in calculated_matches[0]
    assert Module(name=MODULE_A) in calculated_matches[1]
    assert Module(name=MODULE_B) in calculated_matches[1]
    assert Module(name=MODULE_D) in calculated_matches[1]
