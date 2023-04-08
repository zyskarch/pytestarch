from __future__ import annotations

import pytest

from pytestarch import EvaluableArchitecture, LayerRule
from pytestarch.query_language.exceptions import ImproperlyConfigured


def test_architecture_has_to_be_specified_first(
    graph_based_on_string_module_names: EvaluableArchitecture,
) -> None:
    with pytest.raises(
        ImproperlyConfigured,
        match="Specify a LayeredArchitecture before defining layer behavior.",
    ):
        LayerRule().layers_that()
