from __future__ import annotations

import re

import pytest

from pytestarch import EvaluableArchitecture
from pytestarch.eval_structure.evaluable_graph import EvaluableArchitectureGraph
from pytestarch.eval_structure.networkxgraph import NetworkxGraph
from pytestarch.eval_structure_generation.file_import.import_types import AbsoluteImport
from pytestarch.experimental import onion_architecture
from pytestarch.query_language.exceptions import ImproperlyConfigured

DOMAIN_MODEL = "project.domain.model"
DOMAIN_MODEL_2 = "project.domain.model_2"
DOMAIN_SERVICE = "project.domain.service"
APPLICATION_SERVICE = "project.application.service"
CLI_ADAPTER = "project.adapter.cli"
CLI_ADAPTER_SUBMODULE = "project.adapter.cli.http"
REST_ADAPTER = "project.adapter.rest"
OUTSIDE = "project.outside"

ALL_MODULES = [
    DOMAIN_MODEL,
    DOMAIN_SERVICE,
    APPLICATION_SERVICE,
    CLI_ADAPTER,
    CLI_ADAPTER_SUBMODULE,
    REST_ADAPTER,
    OUTSIDE,
    DOMAIN_MODEL_2,
]


def _evaluable(*imports: tuple[str, str]) -> EvaluableArchitecture:
    return EvaluableArchitectureGraph(
        NetworkxGraph(ALL_MODULES, [AbsoluteImport(a, b) for a, b in imports])
    )


def _full_onion():
    return (
        onion_architecture()
        .domain_models(DOMAIN_MODEL)
        .domain_services(DOMAIN_SERVICE)
        .application_services(APPLICATION_SERVICE)
        .adapter("cli", CLI_ADAPTER)
        .adapter("rest", REST_ADAPTER)
    )


# adapter -> application service -> domain service -> domain model
def test_correct_onion_architecture_applies() -> None:
    evaluable = _evaluable(
        (CLI_ADAPTER, APPLICATION_SERVICE),
        (REST_ADAPTER, DOMAIN_SERVICE),
        (APPLICATION_SERVICE, DOMAIN_SERVICE),
        (APPLICATION_SERVICE, DOMAIN_MODEL),
        (CLI_ADAPTER, DOMAIN_MODEL),
        (DOMAIN_SERVICE, DOMAIN_MODEL),
    )

    _full_onion().assert_applies(evaluable)


def test_onion_architecture_passes_if_upper_layers_are_unused() -> None:
    # layer rules created by the onion architecture only forbid access by
    # non-whitelisted modules; they do not require any access to happen
    evaluable = _evaluable((DOMAIN_SERVICE, DOMAIN_MODEL))

    _full_onion().assert_applies(evaluable)


def test_dependencies_within_a_component_are_allowed() -> None:
    onion = (
        onion_architecture()
        .domain_models([DOMAIN_MODEL, DOMAIN_MODEL_2])
        .domain_services(DOMAIN_SERVICE)
        .application_services(APPLICATION_SERVICE)
        .adapter("cli", CLI_ADAPTER)
    )
    evaluable = _evaluable(
        (DOMAIN_MODEL_2, DOMAIN_MODEL),
        (DOMAIN_MODEL, DOMAIN_MODEL_2),
        (CLI_ADAPTER_SUBMODULE, CLI_ADAPTER),
        (CLI_ADAPTER, CLI_ADAPTER_SUBMODULE),
    )

    onion.assert_applies(evaluable)


def test_access_by_module_outside_the_architecture_is_violated() -> None:
    evaluable = _evaluable(
        (OUTSIDE, DOMAIN_MODEL),
        (APPLICATION_SERVICE, DOMAIN_MODEL),  # allowed
    )

    with pytest.raises(
        AssertionError,
        match=re.escape(
            f'"{DOMAIN_MODEL}" (layer "domain model") is imported by "{OUTSIDE}"'
            " (no layer)."
        ),
    ):
        _full_onion().assert_applies(evaluable)


def test_access_of_adapter_is_violated() -> None:
    evaluable = _evaluable(
        (OUTSIDE, CLI_ADAPTER),
    )

    with pytest.raises(
        AssertionError,
        match=re.escape(
            f'"{CLI_ADAPTER}" (layer "cli adapter") is imported by "{OUTSIDE}"'
            " (no layer)."
        ),
    ):
        _full_onion().assert_applies(evaluable)


def test_access_of_adapter_by_another_adapter_is_violated() -> None:
    evaluable = _evaluable(
        (REST_ADAPTER, CLI_ADAPTER),
    )

    with pytest.raises(
        AssertionError,
        match=re.escape(
            f'"{CLI_ADAPTER}" (layer "cli adapter") is imported by '
            f'"{REST_ADAPTER}" (layer "rest adapter").'
        ),
    ):
        _full_onion().assert_applies(evaluable)


def test_access_of_application_service_without_adapters_is_violated() -> None:
    onion = (
        onion_architecture()
        .domain_models(DOMAIN_MODEL)
        .domain_services(DOMAIN_SERVICE)
        .application_services(APPLICATION_SERVICE)
    )
    evaluable = _evaluable(
        (OUTSIDE, APPLICATION_SERVICE),
    )

    with pytest.raises(
        AssertionError,
        match=re.escape(
            f'"{APPLICATION_SERVICE}" (layer "application service") is imported by'
            f' "{OUTSIDE}" (no layer).'
        ),
    ):
        onion.assert_applies(evaluable)


def test_specified_components_are_part_of_the_whitelist() -> None:
    # domain services and adapters may access the domain models even though no
    # application services have been specified
    onion = (
        onion_architecture()
        .domain_models(DOMAIN_MODEL)
        .domain_services(DOMAIN_SERVICE)
        .adapter("cli", CLI_ADAPTER)
    )
    evaluable = _evaluable(
        (DOMAIN_SERVICE, DOMAIN_MODEL),
        (CLI_ADAPTER, DOMAIN_MODEL),
        (CLI_ADAPTER, DOMAIN_SERVICE),
    )

    onion.assert_applies(evaluable)


def test_unspecified_components_are_not_part_of_the_whitelist() -> None:
    # application services have not been specified, so they are not a valid
    # accessor of the domain services either - as they do not belong to any
    # component, their access is a violation
    onion = (
        onion_architecture().domain_models(DOMAIN_MODEL).domain_services(DOMAIN_SERVICE)
    )
    evaluable = _evaluable(
        (APPLICATION_SERVICE, DOMAIN_SERVICE),
    )

    with pytest.raises(
        AssertionError,
        match=re.escape(
            f'"{DOMAIN_SERVICE}" (layer "domain service") is imported by'
            f' "{APPLICATION_SERVICE}" (no layer).'
        ),
    ):
        onion.assert_applies(evaluable)


def test_violations_of_multiple_rules_are_reported_jointly() -> None:
    evaluable = _evaluable(
        (OUTSIDE, DOMAIN_MODEL),
        (OUTSIDE, CLI_ADAPTER),
    )

    with pytest.raises(AssertionError) as error:
        _full_onion().assert_applies(evaluable)

    message = str(error.value)
    assert 'imported by "project.outside" (no layer)' in message
    assert '(layer "domain model")' in message
    assert '(layer "cli adapter")' in message


def test_error_message_starts_with_the_violated_architecture() -> None:
    onion = _full_onion()
    evaluable = _evaluable((OUTSIDE, DOMAIN_MODEL))

    with pytest.raises(AssertionError) as error:
        onion.assert_applies(evaluable)

    assert str(error.value).startswith(f"{onion} was violated:\n")


def test_nothing_specified_raises_error() -> None:
    with pytest.raises(
        ImproperlyConfigured,
        match="Specify at least one component of the onion architecture first.",
    ):
        onion_architecture().assert_applies(_evaluable())

    with pytest.raises(
        ImproperlyConfigured,
        match="Specify at least one component of the onion architecture first.",
    ):
        onion_architecture().layered_architecture()


def test_components_can_only_be_specified_once() -> None:
    with pytest.raises(
        ImproperlyConfigured,
        match="The domain models of the onion architecture are already specified.",
    ):
        onion_architecture().domain_models("A").domain_models("B")


def test_adapters_need_unique_names() -> None:
    with pytest.raises(ImproperlyConfigured, match="Adapter cli already exists."):
        onion_architecture().adapter("cli", "A").adapter("cli", "B")


def test_a_module_can_only_belong_to_one_component() -> None:
    with pytest.raises(
        ImproperlyConfigured, match=r"Module\(s\) A already assigned to a layer."
    ):
        onion_architecture().domain_models("A").domain_services(["A", "B"])

    with pytest.raises(
        ImproperlyConfigured, match=r"Module\(s\) A already assigned to a layer."
    ):
        onion_architecture().domain_models("A").adapter("cli", ["A", "B"])


def test_components_must_contain_at_least_one_module() -> None:
    with pytest.raises(
        ImproperlyConfigured,
        match="The domain models of the onion architecture must contain at least one module.",
    ):
        onion_architecture().domain_models([])

    with pytest.raises(
        ImproperlyConfigured,
        match="The adapter cli of the onion architecture must contain at least one module.",
    ):
        onion_architecture().adapter("cli", [])


def test_layered_architecture_reflects_components() -> None:
    arch = _full_onion().layered_architecture()

    assert str(arch) == (
        "Layered Architecture:"
        f" Layer domain model: [{DOMAIN_MODEL}];"
        f" Layer domain service: [{DOMAIN_SERVICE}];"
        f" Layer application service: [{APPLICATION_SERVICE}];"
        f" Layer cli adapter: [{CLI_ADAPTER}];"
        f" Layer rest adapter: [{REST_ADAPTER}]"
    )


def test_only_adapters_specified_is_valid() -> None:
    evaluable = _evaluable((CLI_ADAPTER, APPLICATION_SERVICE))

    onion_architecture().adapter("cli", CLI_ADAPTER).assert_applies(evaluable)


def test_multiple_modules_per_component() -> None:
    models = [DOMAIN_MODEL, DOMAIN_MODEL_2]
    evaluable = _evaluable((CLI_ADAPTER, DOMAIN_MODEL_2))

    (
        onion_architecture()
        .domain_models(models)
        .domain_services(DOMAIN_SERVICE)
        .application_services(APPLICATION_SERVICE)
        .adapter("cli", CLI_ADAPTER)
        .adapter("rest", REST_ADAPTER)
    ).assert_applies(evaluable)


def test_str_representation() -> None:
    assert str(_full_onion()) == (
        "Onion Architecture:"
        f" domain model: [{DOMAIN_MODEL}];"
        f" domain service: [{DOMAIN_SERVICE}];"
        f" application service: [{APPLICATION_SERVICE}];"
        f" adapter 'cli': [{CLI_ADAPTER}];"
        f" adapter 'rest': [{REST_ADAPTER}]"
    )


def test_str_representation_of_partially_specified_architecture() -> None:
    onion = onion_architecture().domain_models(DOMAIN_MODEL).adapter("cli", CLI_ADAPTER)

    assert str(onion) == (
        "Onion Architecture:"
        f" domain model: [{DOMAIN_MODEL}];"
        " domain service: not specified;"
        " application service: not specified;"
        f" adapter 'cli': [{CLI_ADAPTER}]"
    )
    assert str(onion_architecture()) == (
        "Onion Architecture:"
        " domain model: not specified;"
        " domain service: not specified;"
        " application service: not specified"
    )


def test_layered_architecture_only_contains_specified_components() -> None:
    arch = onion_architecture().domain_models(DOMAIN_MODEL).layered_architecture()

    assert str(arch) == f"Layered Architecture: Layer domain model: [{DOMAIN_MODEL}]"
