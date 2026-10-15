from __future__ import annotations

import re

import pytest

from pytestarch import LayeredArchitecture
from pytestarch.eval_structure.evaluable_graph import EvaluableArchitectureGraph
from pytestarch.eval_structure.networkxgraph import NetworkxGraph
from pytestarch.eval_structure_generation.file_import.import_types import AbsoluteImport
from pytestarch.query_language.base_language import BaseLayeredArchitecture
from pytestarch.query_language.exceptions import ImproperlyConfigured
from pytestarch.query_language.layered_architecture_rule import LayerRule


def test_architecture_as_expected() -> None:
    arch: BaseLayeredArchitecture = (
        LayeredArchitecture()
        .layer("A")
        .containing_modules("M")
        .with_layer()
        .layer("B")
        .containing_modules(["N", "O"])
    )

    assert str(arch) == "Layered Architecture: Layer A: [M]; Layer B: [N, O]"


def test_layer_name_has_to_be_defined_first() -> None:
    with pytest.raises(
        ImproperlyConfigured, match="Specify layer name before specifying its modules."
    ):
        LayeredArchitecture().containing_modules("M1")


def test_layer_name_has_to_be_unique() -> None:
    with pytest.raises(ImproperlyConfigured, match="Layer A already exists."):
        LayeredArchitecture().layer("A").containing_modules("M").layer("A")  # type: ignore


def test_layer_name_has_to_be_followed_by_modules() -> None:
    with pytest.raises(
        ImproperlyConfigured,
        match=re.escape("Specify the modules of layer(s) A first."),
    ):
        LayeredArchitecture().layer("A").layer("B")  # type: ignore


def test_modules_can_only_be_defined_once_per_layer() -> None:
    with pytest.raises(
        ImproperlyConfigured, match="Specify layer name before specifying its modules."
    ):
        LayeredArchitecture().layer("A").containing_modules("M").containing_modules("N")  # type: ignore


def test_one_module_can_only_be_in_one_layer() -> None:
    with pytest.raises(
        ImproperlyConfigured,
        match=re.escape("Module(s) M already assigned to a layer."),
    ):
        LayeredArchitecture().layer("A").containing_modules("M").with_layer().layer(
            "B"
        ).containing_modules(["N", "M"])


def test_one_module_passed_as_string_can_only_be_in_one_layer() -> None:
    with pytest.raises(
        ImproperlyConfigured,
        match=re.escape("Module(s) project.a already assigned to a layer."),
    ):
        LayeredArchitecture().layer("A").containing_modules(
            "project.a"
        ).with_layer().layer("B").containing_modules("project.a")


def test_string_module_argument_is_not_split_into_characters() -> None:
    # a single string argument counts as one module for the duplicate and
    # nested-module checks: 'project.a' neither duplicates an existing 'a' of
    # another layer (regression guard for the character-split set) nor is it
    # nested within it in either direction
    arch: BaseLayeredArchitecture = (
        LayeredArchitecture()
        .layer("A")
        .containing_modules("a")
        .with_layer()
        .layer("B")
        .containing_modules("project.a")
    )

    assert str(arch) == "Layered Architecture: Layer A: [a]; Layer B: [project.a]"


def test_module_nested_in_module_of_other_layer_raises_error() -> None:
    with pytest.raises(
        ImproperlyConfigured,
        match=re.escape(
            "Module(s) project.a.b are a submodule or parent module of a module"
            " assigned to another layer."
        ),
    ):
        LayeredArchitecture().layer("A").containing_modules(
            ["project.a"]
        ).with_layer().layer("B").containing_modules(["project.a.b"])


def test_modules_nested_within_one_layer_are_allowed() -> None:
    arch: BaseLayeredArchitecture = (
        LayeredArchitecture()
        .layer("A")
        .containing_modules(["project.a", "project.a.b"])
    )

    assert str(arch) == "Layered Architecture: Layer A: [project.a, project.a.b]"


LAYER_A = "A"
MODULE_A = "project.a"
MODULE_A_UTILS = "project.a_utils"


def _evaluable(*imports: tuple[str, str]) -> EvaluableArchitectureGraph:
    return EvaluableArchitectureGraph(
        NetworkxGraph(
            [MODULE_A, MODULE_A_UTILS],
            [AbsoluteImport(importer, importee) for importer, importee in imports],
        )
    )


def test_module_with_sibling_prefix_of_layer_module_is_no_layer() -> None:
    architecture: LayeredArchitecture = LayeredArchitecture()
    architecture.layer(LAYER_A).containing_modules([MODULE_A])
    rule = (
        LayerRule()
        .based_on(architecture)
        .layers_that()
        .are_named(LAYER_A)
        .should_not()
        .be_accessed_by_any_layer()
    )
    evaluable = _evaluable((MODULE_A_UTILS, MODULE_A))

    with pytest.raises(AssertionError) as error:
        rule.assert_applies(evaluable)

    message = str(error.value)
    assert f'{MODULE_A_UTILS}" (no layer)' in message


def test_layer_module_importing_sibling_prefix_module_is_no_layer() -> None:
    # mirror of test_module_with_sibling_prefix_of_layer_module_is_no_layer
    # with the import direction reversed: the layer module itself imports the
    # sibling-prefixed module, which belongs to no layer
    architecture: LayeredArchitecture = LayeredArchitecture()
    architecture.layer(LAYER_A).containing_modules([MODULE_A])
    rule = (
        LayerRule()
        .based_on(architecture)
        .layers_that()
        .are_named(LAYER_A)
        .should_not()
        .access_any_layer()
    )
    evaluable = _evaluable((MODULE_A, MODULE_A_UTILS))

    with pytest.raises(AssertionError) as error:
        rule.assert_applies(evaluable)

    message = str(error.value)
    assert f'"{MODULE_A_UTILS}" (no layer)' in message
