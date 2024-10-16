from __future__ import annotations

import resources
from pytestarch.pytestarch import get_evaluable_architecture_for_module_objects
from resources import project_with_nested_external_dependencies


def test_external_dependencies_present() -> None:
    evaluable = get_evaluable_architecture_for_module_objects(
        resources,
        project_with_nested_external_dependencies,
        exclude_external_libraries=False,
    )
    graph = evaluable._graph  # type: ignore[attr-defined]

    assert "logging" in graph
    assert "logging.handlers" in graph


def test_external_dependencies_removed_if_complete_match() -> None:
    evaluable = get_evaluable_architecture_for_module_objects(
        resources,
        project_with_nested_external_dependencies,
        exclude_external_libraries=False,
        regex_external_exclusions=("logging",),
    )
    graph = evaluable._graph  # type: ignore[attr-defined]

    assert "logging" not in graph
    assert "logging.handlers" not in graph


def test_external_dependencies_removed_if_not_complete_match() -> None:
    evaluable = get_evaluable_architecture_for_module_objects(
        resources,
        project_with_nested_external_dependencies,
        exclude_external_libraries=False,
        regex_external_exclusions=("logging$",),
    )
    graph = evaluable._graph  # type: ignore[attr-defined]

    assert "logging" not in graph
    assert "logging.handlers" not in graph  # parent is excluded


def test_external_dependencies_removed_if_partial_match() -> None:
    evaluable = get_evaluable_architecture_for_module_objects(
        resources,
        project_with_nested_external_dependencies,
        exclude_external_libraries=False,
        regex_external_exclusions=("logging.*",),
    )
    graph = evaluable._graph  # type: ignore[attr-defined]

    assert "logging" not in graph
    assert "logging.handlers" not in graph


def test_external_dependencies_removed_if_complete_pseudo_regex_match() -> None:
    evaluable = get_evaluable_architecture_for_module_objects(
        resources,
        project_with_nested_external_dependencies,
        exclude_external_libraries=False,
        external_exclusions=("logging",),
    )
    graph = evaluable._graph  # type: ignore[attr-defined]

    assert "logging" not in graph
    assert "logging.handlers" not in graph  # parent is excluded


def test_external_dependencies_removed_if_partial_pseudo_regex_match() -> None:
    evaluable = get_evaluable_architecture_for_module_objects(
        resources,
        project_with_nested_external_dependencies,
        exclude_external_libraries=False,
        external_exclusions=("logging*",),
    )
    graph = evaluable._graph  # type: ignore[attr-defined]

    assert "logging" not in graph
    assert "logging.handlers" not in graph
