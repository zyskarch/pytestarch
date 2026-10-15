from __future__ import annotations

import pytest

from pytestarch.eval_structure.evaluable_architecture import (
    LayerMapping,
    ModuleNameFilter,
)
from pytestarch.eval_structure.exceptions import LayerMismatch


def _mapping(layers: dict[str, list[str]]) -> LayerMapping:
    return LayerMapping(
        {
            layer: [ModuleNameFilter(name=module) for module in modules]
            for layer, modules in layers.items()
        }
    )


def test_exact_match_returns_layer() -> None:
    mapping = _mapping({"A": ["project.model"]})

    assert mapping.get_layer_for_module_name("project.model") == "A"


def test_dotted_submodule_returns_parent_layer() -> None:
    mapping = _mapping({"A": ["project.model"]})

    assert mapping.get_layer_for_module_name("project.model.core") == "A"


def test_prefix_sibling_does_not_match() -> None:
    mapping = _mapping({"A": ["project.model"]})

    assert mapping.get_layer_for_module_name("project.model_utils") is None


def test_sibling_prefix_layers_do_not_raise() -> None:
    mapping = _mapping({"A": ["project.a"], "B": ["project.ab"]})

    assert mapping.get_layer_for_module_name("project.abc") is None


def test_module_nested_in_modules_of_different_layers_is_ambiguous() -> None:
    # retained by design: a module nested below layer modules of different layers
    # has no unambiguous parent layer
    mapping = _mapping({"A": ["project.a"], "B": ["project.a.b"]})

    with pytest.raises(LayerMismatch):
        mapping.get_layer_for_module_name("project.a.b.c")


def test_nested_modules_within_one_layer_are_unambiguous() -> None:
    mapping = _mapping({"A": ["project.x", "project.x.sub"]})

    assert mapping.get_layer_for_module_name("project.x.sub.deep") == "A"
