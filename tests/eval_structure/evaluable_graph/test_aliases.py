from __future__ import annotations

import pytest
from matplotlib.pyplot import subplots

from eval_structure.conftest import (
    MODULE_1,
    MODULE_2,
    MODULE_A,
    MODULE_E,
    SUB_MODULE_OF_2,
)
from pytestarch import EvaluableArchitecture
from pytestarch.eval_structure.evaluable_graph import EvaluableArchitectureGraph
from pytestarch.eval_structure.networkxgraph import NetworkxGraph


def test_all_modules_labeled_when_aliases_used(
    evaluable: EvaluableArchitecture,
) -> None:
    module_1_alias = "1"
    aliases = {MODULE_1: module_1_alias}
    fig, ax = subplots()

    evaluable.visualize(aliases=aliases, ax=ax)

    labels_in_plot = [t.get_text() for t in ax.texts]
    assert len(labels_in_plot) == 6


def test_alias_replaces_module_name_in_plot(evaluable: EvaluableArchitecture) -> None:
    module_2_alias = "2"
    aliases = {MODULE_2: module_2_alias}
    submodule_label_with_alias = f"{module_2_alias}.SubModule1"
    fig, ax = subplots()

    evaluable.visualize(aliases=aliases, ax=ax)

    labels_in_plot = [t.get_text() for t in ax.texts]
    assert module_2_alias in labels_in_plot
    assert MODULE_2 not in labels_in_plot
    assert SUB_MODULE_OF_2 not in labels_in_plot
    assert submodule_label_with_alias in labels_in_plot


def test_when_module_and_a_submodule_have_aliases_the_submodule_alias_takes_priority(
    submodule_evaluable: EvaluableArchitecture,
) -> None:
    module_e_alias = "e"
    submodule_of_e_alias = "ea"
    submodule_label_with_parent_alias = f"{module_e_alias}.A"
    aliases = {MODULE_E: module_e_alias, MODULE_A: submodule_of_e_alias}
    fig, ax = subplots()

    submodule_evaluable.visualize(aliases=aliases, ax=ax)

    labels_in_plot = [t.get_text() for t in ax.texts]
    assert module_e_alias in labels_in_plot
    assert submodule_of_e_alias in labels_in_plot
    assert submodule_label_with_parent_alias not in labels_in_plot
    assert f"{module_e_alias}.F" in labels_in_plot


def test_when_module_name_in_alias_spec_is_not_found_an_error_is_raised(
    evaluable: EvaluableArchitecture,
) -> None:
    non_existent_module = "non_existent_module"
    aliases = {non_existent_module: "a"}

    with pytest.raises(KeyError, match=non_existent_module):
        evaluable.visualize(aliases=aliases)


ALIASED_MODULE = "app"
SUB_MODULE_OF_ALIASED_MODULE = "app.web"
MODULE_WITH_SAME_NAME_PREFIX = "appdirs"
MODULE_WITH_SAME_NAME_PREFIX_2 = "appdirs2"


@pytest.fixture(scope="module")
def sibling_prefix_evaluable() -> EvaluableArchitectureGraph:
    all_modules = [
        ALIASED_MODULE,
        SUB_MODULE_OF_ALIASED_MODULE,
        MODULE_WITH_SAME_NAME_PREFIX,
        MODULE_WITH_SAME_NAME_PREFIX_2,
    ]

    return EvaluableArchitectureGraph(NetworkxGraph(all_modules, []))


def test_alias_does_not_relabel_module_sharing_name_prefix_without_dot_boundary(
    sibling_prefix_evaluable: EvaluableArchitecture,
) -> None:
    module_alias = "A"
    aliases = {ALIASED_MODULE: module_alias}
    fig, ax = subplots()

    sibling_prefix_evaluable.visualize(aliases=aliases, ax=ax)

    labels_in_plot = [t.get_text() for t in ax.texts]
    assert len(labels_in_plot) == 4
    assert module_alias in labels_in_plot
    assert f"{module_alias}.web" in labels_in_plot
    assert MODULE_WITH_SAME_NAME_PREFIX in labels_in_plot
    assert MODULE_WITH_SAME_NAME_PREFIX_2 in labels_in_plot
    assert f"{module_alias}dirs" not in labels_in_plot
    assert f"{module_alias}dirs2" not in labels_in_plot


def test_prefix_sibling_alias_keys_are_applied_to_their_own_modules_only(
    sibling_prefix_evaluable: EvaluableArchitecture,
) -> None:
    module_alias = "A"
    prefix_sibling_alias = "D"
    aliases = {
        ALIASED_MODULE: module_alias,
        MODULE_WITH_SAME_NAME_PREFIX: prefix_sibling_alias,
    }
    fig, ax = subplots()

    sibling_prefix_evaluable.visualize(aliases=aliases, ax=ax)

    labels_in_plot = [t.get_text() for t in ax.texts]
    assert len(labels_in_plot) == 4
    assert module_alias in labels_in_plot
    assert f"{module_alias}.web" in labels_in_plot
    assert prefix_sibling_alias in labels_in_plot
    assert MODULE_WITH_SAME_NAME_PREFIX_2 in labels_in_plot
    assert f"{prefix_sibling_alias}2" not in labels_in_plot
