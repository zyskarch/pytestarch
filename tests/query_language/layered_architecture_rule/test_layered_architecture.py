from __future__ import annotations

import re

import pytest

from pytestarch import LayeredArchitecture
from pytestarch.query_language.exceptions import ImproperlyConfigured


def test_architecture_as_expected() -> None:
    arch = (
        LayeredArchitecture()
        .layer("A")
        .containing_modules("M")
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
        LayeredArchitecture().layer("A").containing_modules("M").layer("A")


def test_layer_name_has_to_be_followed_by_modules() -> None:
    with pytest.raises(
        ImproperlyConfigured,
        match=re.escape("Specify the modules of layer(s) A first."),
    ):
        LayeredArchitecture().layer("A").layer("B")


def test_modules_can_only_be_defined_once_per_layer() -> None:
    with pytest.raises(
        ImproperlyConfigured, match="Specify layer name before specifying its modules."
    ):
        LayeredArchitecture().layer("A").containing_modules("M").containing_modules("N")


def test_one_module_can_only_be_in_one_layer() -> None:
    with pytest.raises(
        ImproperlyConfigured,
        match=re.escape("Module(s) M already assigned to a layer."),
    ):
        LayeredArchitecture().layer("A").containing_modules("M").layer(
            "B"
        ).containing_modules(["N", "M"])
