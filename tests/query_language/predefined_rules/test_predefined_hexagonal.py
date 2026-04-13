from __future__ import annotations

import pytest

from pytestarch import EvaluableArchitecture, HexagonalArchitecture
from pytestarch.query_language.exceptions import ImproperlyConfigured

# Fully-qualified module names from flat_test_project_1.
MODEL = "flat_test_project_1.model"
UTIL = "flat_test_project_1.util"
LOGGING_UTIL = "flat_test_project_1.logging_util"
EXPORTER = "flat_test_project_1.exporter"
PERSISTENCE = "flat_test_project_1.persistence"
SERVICES = "flat_test_project_1.services"
IMPORTER = "flat_test_project_1.importer"


def test_builder_returns_self_for_chaining() -> None:
    arch = HexagonalArchitecture()
    assert arch.domain_models(MODEL) is arch
    assert arch.domain_services(UTIL) is arch
    assert arch.application_services(LOGGING_UTIL) is arch
    assert arch.adapter("rest", EXPORTER) is arch


def test_assert_applies_returns_none_on_valid_architecture(
    flat_project_1: EvaluableArchitecture,
) -> None:
    # model imports nothing - valid as domain_models
    # util imports nothing - valid as domain_services (may access domain_models)
    # logging_util imports only util (domain_services) - valid as application_services
    result = (
        HexagonalArchitecture()
        .domain_models(MODEL)
        .domain_services(UTIL)
        .application_services(LOGGING_UTIL)
        .assert_applies(flat_project_1)
    )
    assert result is None


def test_domain_models_must_not_access_other_configured_layers(
    flat_project_1: EvaluableArchitecture,
) -> None:
    # logging_util imports util - if util is a domain_services layer and logging_util is
    # domain_models, that violates the rule that domain_models can't access domain_services
    with pytest.raises(AssertionError):
        (
            HexagonalArchitecture()
            .domain_models(LOGGING_UTIL)
            .domain_services(UTIL)
            .assert_applies(flat_project_1)
        )


def test_application_services_must_not_access_adapter(
    flat_project_1: EvaluableArchitecture,
) -> None:
    # persistence imports model - if model is an adapter and persistence is application_services,
    # then application_services accesses adapter, which violates hexagonal rules
    with pytest.raises(AssertionError):
        (
            HexagonalArchitecture()
            .domain_models(UTIL)
            .application_services(PERSISTENCE)
            .adapter("model", MODEL)
            .assert_applies(flat_project_1)
        )


def test_partial_configuration_only_domain_models(
    flat_project_1: EvaluableArchitecture,
) -> None:
    # Only domain_models configured - model imports nothing, should pass
    HexagonalArchitecture().domain_models(MODEL).assert_applies(flat_project_1)


def test_empty_configuration_passes(flat_project_1: EvaluableArchitecture) -> None:
    # No layers configured - no rules, always passes
    HexagonalArchitecture().assert_applies(flat_project_1)


def test_multiple_adapters_are_independent_layers(
    flat_project_1: EvaluableArchitecture,
) -> None:
    # model and util each import nothing - valid as separate adapters when
    # no inner layers are configured (adapters may access configured inner layers,
    # but if none exist, the allowed list is empty so adapters must import nothing)
    HexagonalArchitecture().adapter("a", MODEL).adapter("b", UTIL).assert_applies(
        flat_project_1
    )


def test_adapter_with_no_modules_raises() -> None:
    with pytest.raises(ImproperlyConfigured, match="rest"):
        HexagonalArchitecture().adapter("rest")


def test_full_hexagonal_architecture_passes(
    flat_project_1: EvaluableArchitecture,
) -> None:
    # model: no imports -> valid domain_models
    # util: no imports -> valid domain_services (allowed: domain_models=model)
    # logging_util: imports util only -> valid application_services (allowed: model, util)
    # importer: imports model, util -> valid adapter (allowed: model, util, logging_util)
    (
        HexagonalArchitecture()
        .domain_models(MODEL)
        .domain_services(UTIL)
        .application_services(LOGGING_UTIL)
        .adapter("importer", IMPORTER)
        .assert_applies(flat_project_1)
    )
