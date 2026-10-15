from __future__ import annotations

import re
from collections.abc import Sequence

import pytest

from pytestarch import EvaluableArchitecture, LayeredArchitecture, LayerRule
from pytestarch.eval_structure.evaluable_graph import EvaluableArchitectureGraph
from pytestarch.eval_structure.networkxgraph import NetworkxGraph
from pytestarch.eval_structure_generation.file_import.import_types import AbsoluteImport
from pytestarch.experimental import (
    PredefinedLayeredArchitecture,
    layered_architecture,
)
from pytestarch.query_language.exceptions import ImproperlyConfigured
from pytestarch.query_language.multiple_rule_applier import MultipleRuleApplier

MODULE_A = "project.a"
MODULE_A_2 = "project.a_2"
MODULE_B = "project.b"
MODULE_C = "project.c"
UNRELATED = "project.unrelated"

LAYER_A = "A"
LAYER_B = "B"
LAYER_C = "C"

ALL_MODULES = [MODULE_A, MODULE_A_2, MODULE_B, MODULE_C, UNRELATED]


def _evaluable(*imports: tuple[str, str]) -> EvaluableArchitecture:
    return EvaluableArchitectureGraph(
        NetworkxGraph(ALL_MODULES, [AbsoluteImport(a, b) for a, b in imports])
    )


def _three_layers(
    allowed_dependencies: dict[str, str | Sequence[str]],
) -> PredefinedLayeredArchitecture:
    return layered_architecture(
        layers={LAYER_A: MODULE_A, LAYER_B: MODULE_B, LAYER_C: MODULE_C},
        allowed_dependencies=allowed_dependencies,
    )


# layer A may only access layers B and C; B and C are unrestricted
def test_layers_only_import_their_allowed_layers() -> None:
    rules = _three_layers({LAYER_A: [LAYER_B, LAYER_C]})
    evaluable = _evaluable(
        (MODULE_A, MODULE_B),
        (MODULE_A, MODULE_C),
        (MODULE_B, UNRELATED),
    )

    rules.assert_applies(evaluable)


def test_layers_omitted_from_allowed_dependencies_are_unrestricted() -> None:
    rules = _three_layers({LAYER_A: [LAYER_B]})
    evaluable = _evaluable(
        (MODULE_A, MODULE_B),
        (MODULE_B, MODULE_C),  # may import another layer
        (MODULE_B, UNRELATED),  # and modules outside the architecture
        (MODULE_C, UNRELATED),
    )

    rules.assert_applies(evaluable)


def test_dependencies_within_a_layer_are_allowed() -> None:
    rules = layered_architecture(
        layers={LAYER_A: [MODULE_A, MODULE_A_2]},
        allowed_dependencies={LAYER_A: []},
    )
    evaluable = _evaluable((MODULE_A, MODULE_A_2), (MODULE_A_2, MODULE_A))

    rules.assert_applies(evaluable)


def test_import_of_non_whitelisted_layer_is_violated() -> None:
    rules = _three_layers({LAYER_A: [LAYER_B]})
    evaluable = _evaluable((MODULE_A, MODULE_C))

    with pytest.raises(
        AssertionError,
        match=re.escape(
            f'"{MODULE_A}" (layer "{LAYER_A}") imports "{MODULE_C}"'
            f' (layer "{LAYER_C}").'
        ),
    ):
        rules.assert_applies(evaluable)


def test_import_of_module_without_layer_is_violated() -> None:
    rules = _three_layers({LAYER_A: [LAYER_B]})
    evaluable = _evaluable((MODULE_A, UNRELATED))

    with pytest.raises(
        AssertionError,
        match=re.escape(
            f'"{MODULE_A}" (layer "{LAYER_A}") imports "{UNRELATED}" (no layer).'
        ),
    ):
        rules.assert_applies(evaluable)


def test_empty_allowlist_forbids_all_outbound_dependencies() -> None:
    rules = _three_layers({LAYER_A: []})
    evaluable = _evaluable((MODULE_A, MODULE_B), (MODULE_A, UNRELATED))

    with pytest.raises(AssertionError) as error:
        rules.assert_applies(evaluable)

    message = str(error.value)
    assert f'imports "{MODULE_B}" (layer "{LAYER_B}").' in message
    assert f'imports "{UNRELATED}" (no layer).' in message


def test_no_allowed_dependencies_generates_no_rules() -> None:
    rules = _three_layers({})
    evaluable = _evaluable(
        (MODULE_A, MODULE_B),
        (MODULE_B, MODULE_C),
        (MODULE_C, UNRELATED),
    )

    assert isinstance(rules, PredefinedLayeredArchitecture)
    assert isinstance(rules, MultipleRuleApplier)

    # in particular, nothing raises
    rules.assert_applies(evaluable)


def test_layer_name_as_allowed_dependency_is_normalized() -> None:
    rules = layered_architecture(
        layers={LAYER_A: MODULE_A, LAYER_B: MODULE_B},
        allowed_dependencies={LAYER_A: LAYER_B},
    )
    evaluable = _evaluable((MODULE_A, MODULE_B))

    rules.assert_applies(evaluable)


def test_import_beyond_single_layer_name_allowed_dependency_is_violated() -> None:
    rules = layered_architecture(
        layers={LAYER_A: MODULE_A, LAYER_B: MODULE_B},
        allowed_dependencies={LAYER_A: LAYER_B},
    )
    evaluable = _evaluable((MODULE_A, UNRELATED))

    with pytest.raises(
        AssertionError,
        match=re.escape(
            f'"{MODULE_A}" (layer "{LAYER_A}") imports "{UNRELATED}" (no layer).'
        ),
    ):
        rules.assert_applies(evaluable)


def test_tuple_of_modules_is_accepted() -> None:
    rules = layered_architecture(
        layers={LAYER_A: (MODULE_A,)},
        allowed_dependencies={},
    )
    evaluable = _evaluable()

    rules.assert_applies(evaluable)


def test_tuple_of_layer_names_is_accepted_as_allowed_dependency() -> None:
    rules = layered_architecture(
        layers={LAYER_A: MODULE_A, LAYER_B: MODULE_B},
        allowed_dependencies={LAYER_A: (LAYER_B,)},
    )
    evaluable = _evaluable((MODULE_A, MODULE_B))

    rules.assert_applies(evaluable)


def test_unknown_subject_layer_raises_error() -> None:
    with pytest.raises(
        ImproperlyConfigured,
        match=re.escape(
            "Layer(s) D referenced in allowed_dependencies are not defined in layers."
        ),
    ):
        layered_architecture(
            layers={LAYER_A: MODULE_A},
            allowed_dependencies={"D": [LAYER_A]},
        )


def test_unknown_allowed_dependency_raises_error() -> None:
    with pytest.raises(
        ImproperlyConfigured,
        match=re.escape(
            "Layer(s) D referenced as allowed dependencies are not defined in layers."
        ),
    ):
        layered_architecture(
            layers={LAYER_A: MODULE_A, LAYER_B: MODULE_B},
            allowed_dependencies={LAYER_A: [LAYER_B, "D"]},
        )


def test_empty_module_list_raises_error_at_construction() -> None:
    with pytest.raises(
        ImproperlyConfigured,
        match="Layer A must contain at least one module.",
    ):
        layered_architecture(
            layers={LAYER_A: [], LAYER_B: MODULE_B}, allowed_dependencies={}
        )


def test_empty_layers_mapping_raises_error() -> None:
    with pytest.raises(
        ImproperlyConfigured,
        match="Specify at least one layer",
    ):
        layered_architecture({}, {})


def test_a_module_can_only_belong_to_one_layer() -> None:
    with pytest.raises(
        ImproperlyConfigured,
        match=re.escape("Module(s) project.a already assigned to a layer."),
    ):
        layered_architecture(
            layers={LAYER_A: [MODULE_A, MODULE_A_2], LAYER_B: [MODULE_A, MODULE_B]},
            allowed_dependencies={},
        )


def test_duplicate_module_error_is_sorted_deterministically() -> None:
    with pytest.raises(
        ImproperlyConfigured,
        match=re.escape("Module(s) a, b already assigned to a layer."),
    ):
        layered_architecture(
            layers={LAYER_A: ["a", "b"], LAYER_B: ["b", "a"]},
            allowed_dependencies={LAYER_A: []},
        )


def test_duplicate_module_within_a_layer_is_deduplicated() -> None:
    rules = layered_architecture(
        layers={LAYER_A: [MODULE_A, MODULE_A], LAYER_B: MODULE_B},
        allowed_dependencies={LAYER_A: []},
    )

    assert str(rules).count(f"layer '{LAYER_A}': [{MODULE_A}]") == 1


def test_error_message_starts_with_the_violated_architecture() -> None:
    rules = _three_layers({LAYER_A: [LAYER_B]})
    evaluable = _evaluable((MODULE_A, MODULE_C))

    with pytest.raises(AssertionError) as error:
        rules.assert_applies(evaluable)

    assert str(error.value).startswith(f"{rules} was violated:\n")


def test_violations_of_multiple_layers_are_reported_jointly() -> None:
    rules = _three_layers({LAYER_A: [], LAYER_B: []})
    evaluable = _evaluable((MODULE_A, MODULE_C), (MODULE_B, MODULE_C))

    with pytest.raises(AssertionError) as error:
        rules.assert_applies(evaluable)

    message = str(error.value)
    assert (
        f'"{MODULE_A}" (layer "{LAYER_A}") imports "{MODULE_C}" (layer "{LAYER_C}").'
    ) in message
    assert (
        f'"{MODULE_B}" (layer "{LAYER_B}") imports "{MODULE_C}" (layer "{LAYER_C}").'
    ) in message


def test_layered_architecture_reflects_the_defined_layers() -> None:
    rules = layered_architecture(
        layers={LAYER_A: [MODULE_A, MODULE_A_2], LAYER_B: MODULE_B},
        allowed_dependencies={LAYER_A: [LAYER_B]},
    )

    equivalent_architecture = (
        LayeredArchitecture()
        .layer(LAYER_A)
        .containing_modules([MODULE_A, MODULE_A_2])
        .with_layer()
        .layer(LAYER_B)
        .containing_modules([MODULE_B])
    )

    assert str(rules.layered_architecture()) == str(equivalent_architecture)


def test_layer_rule_can_be_based_on_the_layered_architecture() -> None:
    rules = layered_architecture(
        layers={LAYER_A: MODULE_A, LAYER_B: MODULE_B},
        allowed_dependencies={},
    )
    arch = rules.layered_architecture()

    layer_rule = (
        LayerRule()
        .based_on(arch)
        .layers_that()
        .are_named(LAYER_B)
        .should_not()
        .access_any_layer()
    )

    layer_rule.assert_applies(_evaluable())

    evaluable = _evaluable((MODULE_B, MODULE_A))
    with pytest.raises(
        AssertionError,
        match=re.escape(
            f'"{MODULE_B}" (layer "{LAYER_B}") imports "{MODULE_A}"'
            f' (layer "{LAYER_A}").'
        ),
    ):
        layer_rule.assert_applies(evaluable)


def test_str_representation() -> None:
    rules = layered_architecture(
        layers={LAYER_A: [MODULE_A, MODULE_A_2], LAYER_B: MODULE_B},
        allowed_dependencies={LAYER_A: [LAYER_B]},
    )

    assert str(rules) == (
        "Layered Architecture:"
        f" layer '{LAYER_A}': [{MODULE_A}, {MODULE_A_2}];"
        f" layer '{LAYER_B}': [{MODULE_B}]"
    )
