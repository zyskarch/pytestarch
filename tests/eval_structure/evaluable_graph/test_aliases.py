import pytest
from eval_structure.evaluable_graph.conftest import (
    MODULE_1,
    MODULE_2,
    MODULE_A,
    MODULE_E,
    SUB_MODULE_OF_2,
)
from matplotlib.pyplot import subplots

from pytestarch import EvaluableArchitecture


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
    fig, ax = subplots()

    evaluable.visualize(aliases=aliases, ax=ax)

    labels_in_plot = [t.get_text() for t in ax.texts]
    assert module_2_alias in labels_in_plot
    assert MODULE_2 not in labels_in_plot
    assert SUB_MODULE_OF_2 not in labels_in_plot
    assert f"{module_2_alias}.SubModule1" in labels_in_plot


def test_alias_replaces_module_name_in_submodules_plot(
    evaluable: EvaluableArchitecture,
) -> None:
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
    assert SUB_MODULE_OF_2 not in labels_in_plot
    assert submodule_label_with_parent_alias not in labels_in_plot
    assert f"{module_e_alias}.F" in labels_in_plot


def test_when_module_name_in_alias_spec_is_not_found_an_error_is_raised(
    evaluable: EvaluableArchitecture,
) -> None:
    non_existent_module = "non_existent_module"
    aliases = {non_existent_module: "a"}

    with pytest.raises(KeyError, match=non_existent_module):
        evaluable.visualize(aliases=aliases)
