from __future__ import annotations

from collections.abc import Callable

import pytest

from pytestarch.eval_structure.evaluable_architecture import ModuleNameFilter
from pytestarch.eval_structure.evaluable_graph import EvaluableArchitectureGraph
from pytestarch.eval_structure.networkxgraph import NetworkxGraph
from pytestarch.query_language.layered_architecture_rule import (
    LayeredArchitecture,
    LayerRule,
)

MODULE_1 = "M"
MODULE_2 = "N"
MODULE_3 = "O"
MODULE_4 = "P"
MODULE_5 = "Q.*.q"

LAYER_1 = "L1"
LAYER_2 = "L2"
LAYER_3 = "L3"

arch: LayeredArchitecture = (
    LayeredArchitecture()
    .layer(LAYER_1)
    .containing_modules([MODULE_1, MODULE_2])
    .layer(LAYER_2)
    .containing_modules([MODULE_3, MODULE_4])
    .layer(LAYER_3)
    .have_modules_with_names_matching(MODULE_5)
)


def _layer_rule_subject() -> LayerRule:
    return LayerRule().based_on(arch).layers_that().are_named(LAYER_1)  # type: ignore


layer_rule_conversion_test_cases = [
    pytest.param(
        lambda: _layer_rule_subject(),
        {
            "modules_to_check": [
                ModuleNameFilter(name=MODULE_1),
                ModuleNameFilter(name=MODULE_2),
            ],
        },
        id="subject",
    ),
    pytest.param(
        lambda: _layer_rule_subject().should().access_layers_that().are_named(LAYER_2),
        {
            "modules_to_check_against": [
                ModuleNameFilter(name=MODULE_3),
                ModuleNameFilter(name=MODULE_4),
            ],
        },
        id="object",
    ),
    pytest.param(
        lambda: _layer_rule_subject().should().access_layers_that().are_named(LAYER_2),
        {"should": True, "should_only": False, "should_not": False},
        id="should",
    ),
    pytest.param(
        lambda: (
            _layer_rule_subject().should_only().access_layers_that().are_named(LAYER_2)
        ),
        {"should": False, "should_only": True, "should_not": False},
        id="should_only",
    ),
    pytest.param(
        lambda: (
            _layer_rule_subject().should_not().access_layers_that().are_named(LAYER_2)
        ),
        {"should": False, "should_only": False, "should_not": True},
        id="should_not",
    ),
    pytest.param(
        lambda: _layer_rule_subject().should().access_layers_that().are_named(LAYER_2),
        {"except_present": False, "import_": True},
        id="access",
    ),
    pytest.param(
        lambda: (
            _layer_rule_subject()
            .should()
            .be_accessed_by_layers_that()
            .are_named(LAYER_2)
        ),
        {"except_present": False, "import_": False},
        id="be_accessed",
    ),
    pytest.param(
        lambda: (
            _layer_rule_subject()
            .should()
            .access_layers_except_layers_that()
            .are_named(LAYER_2)
        ),
        {"except_present": True, "import_": True},
        id="access_except",
    ),
    pytest.param(
        lambda: (
            _layer_rule_subject()
            .should()
            .be_accessed_by_layers_except_layers_that()
            .are_named(LAYER_2)
        ),
        {"except_present": True, "import_": False},
        id="be_accessed_except",
    ),
    pytest.param(
        lambda: _layer_rule_subject().should().access_any_layer(),
        {"except_present": False, "import_": True, "rule_object_anything": True},
        id="access_any",
    ),
    pytest.param(
        lambda: _layer_rule_subject().should().be_accessed_by_any_layer(),
        {"except_present": False, "import_": False, "rule_object_anything": True},
        id="be_accessed_by_any",
    ),
]


@pytest.mark.parametrize(
    "rule_builder, expected_config_fields", layer_rule_conversion_test_cases
)
def test_layer_rule_converted_to_rule_configuration(
    rule_builder: Callable[[], LayerRule],
    expected_config_fields: dict[str, bool | list[ModuleNameFilter]],
) -> None:
    rule = rule_builder()

    rule_config = rule._rule._configuration  # type: ignore

    for field, expected_value in expected_config_fields.items():
        assert getattr(rule_config, field) == expected_value


def test_not_need_to_use_every_regex_layer_to_apply() -> None:
    all_modules = [
        MODULE_1,
        MODULE_2,
        MODULE_3,
        MODULE_4,
        MODULE_5,
    ]
    imports = []  # type: ignore
    evaluable_graph = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    with pytest.raises(
        AssertionError, match='Layer "L1" is not imported by layer "L2"'
    ):
        _ = (
            LayerRule()
            .based_on(arch)
            .layers_that()
            .are_named(LAYER_1)
            .should_only()
            .be_accessed_by_layers_that()
            .are_named([LAYER_2])
            .assert_applies(evaluable_graph)
        )
