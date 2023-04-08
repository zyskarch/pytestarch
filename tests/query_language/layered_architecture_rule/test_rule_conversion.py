from __future__ import annotations

from pytestarch.eval_structure.evaluable_architecture import Module
from pytestarch.query_language.layered_architecture_rule import (
    LayeredArchitecture,
    LayerRule,
)

MODULE_1 = "M"
MODULE_2 = "N"
MODULE_3 = "O"
MODULE_4 = "P"
MODULE_5 = "Q"

LAYER_1 = "L1"
LAYER_2 = "L2"

arch = (
    LayeredArchitecture()
    .layer(LAYER_1)
    .containing_modules([MODULE_1, MODULE_2])
    .layer(LAYER_2)
    .containing_modules([MODULE_3, MODULE_4, MODULE_5])
)


def test_layer_rule_subject_converted_to_layer_modules() -> None:
    rule = LayerRule().based_on(arch).layers_that().are_named(LAYER_1)

    rule_config = rule._rule._configuration

    expected_modules_to_check = [
        Module(name=MODULE_1, parent_module=None, partial_match=False),
        Module(name=MODULE_2, parent_module=None, partial_match=False),
    ]

    assert rule_config.modules_to_check == expected_modules_to_check


def test_layer_rule_object_converted_to_layer_modules() -> None:
    rule = (
        LayerRule()
        .based_on(arch)
        .layers_that()
        .are_named(LAYER_1)
        .should()
        .access_layers_that()
        .are_named(LAYER_2)
    )

    rule_config = rule._rule._configuration

    expected_modules_to_check = [
        Module(name=MODULE_3, parent_module=None, partial_match=False),
        Module(name=MODULE_4, parent_module=None, partial_match=False),
        Module(name=MODULE_5, parent_module=None, partial_match=False),
    ]

    assert rule_config.modules_to_check_against == expected_modules_to_check


def test_should_converted_correctly() -> None:
    rule = (
        LayerRule()
        .based_on(arch)
        .layers_that()
        .are_named(LAYER_1)
        .should()
        .access_layers_that()
        .are_named(LAYER_2)
    )

    rule_config = rule._rule._configuration

    assert rule_config.should
    assert not rule_config.should_only
    assert not rule_config.should_not


def test_should_not_converted_correctly() -> None:
    rule = (
        LayerRule()
        .based_on(arch)
        .layers_that()
        .are_named(LAYER_1)
        .should_not()
        .access_layers_that()
        .are_named(LAYER_2)
    )

    rule_config = rule._rule._configuration

    assert not rule_config.should
    assert not rule_config.should_only
    assert rule_config.should_not


def test_should_only_converted_correctly() -> None:
    rule = (
        LayerRule()
        .based_on(arch)
        .layers_that()
        .are_named(LAYER_1)
        .should_only()
        .access_layers_that()
        .are_named(LAYER_2)
    )

    rule_config = rule._rule._configuration

    assert not rule_config.should
    assert rule_config.should_only
    assert not rule_config.should_not


def test_access_converted_correctly() -> None:
    rule = (
        LayerRule()
        .based_on(arch)
        .layers_that()
        .are_named(LAYER_1)
        .should()
        .access_layers_that()
        .are_named(LAYER_2)
    )

    rule_config = rule._rule._configuration

    assert not rule_config.except_present
    assert rule_config.import_


def test_be_accessed_converted_correctly() -> None:
    rule = (
        LayerRule()
        .based_on(arch)
        .layers_that()
        .are_named(LAYER_1)
        .should()
        .be_accessed_by_layers_that()
        .are_named(LAYER_2)
    )

    rule_config = rule._rule._configuration

    assert not rule_config.except_present
    assert not rule_config.import_


def test_access_except_converted_correctly() -> None:
    rule = (
        LayerRule()
        .based_on(arch)
        .layers_that()
        .are_named(LAYER_1)
        .should()
        .access_layers_except_layers_that()
        .are_named(LAYER_2)
    )

    rule_config = rule._rule._configuration

    assert rule_config.except_present
    assert rule_config.import_


def test_be_accessed_except_converted_correctly() -> None:
    rule = (
        LayerRule()
        .based_on(arch)
        .layers_that()
        .are_named(LAYER_1)
        .should()
        .be_accessed_by_layers_except_layers_that()
        .are_named(LAYER_2)
    )

    rule_config = rule._rule._configuration

    assert rule_config.except_present
    assert not rule_config.import_


def test_access_any_converted_correctly() -> None:
    rule = (
        LayerRule()
        .based_on(arch)
        .layers_that()
        .are_named(LAYER_1)
        .should()
        .access_any_layer()
    )

    rule_config = rule._rule._configuration

    assert not rule_config.except_present
    assert rule_config.import_
    assert rule_config.rule_object_anything


def test_be_accessed_by_any_converted_correctly() -> None:
    rule = (
        LayerRule()
        .based_on(arch)
        .layers_that()
        .are_named(LAYER_1)
        .should()
        .be_accessed_by_any_layer()
    )

    rule_config = rule._rule._configuration

    assert not rule_config.except_present
    assert not rule_config.import_
    assert rule_config.rule_object_anything
