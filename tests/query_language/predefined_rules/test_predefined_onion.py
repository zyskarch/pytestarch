from __future__ import annotations

import pytest

from pytestarch import EvaluableArchitecture, onion_architecture
from pytestarch.query_language.multiple_rule_applier import MultipleRuleApplier

# Fully-qualified module names from flat_test_project_1.
# We map:
#   domain        -> model (imports nothing)
#   application   -> logging_util (imports only util, which is outside the architecture)
#   infrastructure -> exporter (imports logging_util, model, util)
MODEL = "flat_test_project_1.model"
UTIL = "flat_test_project_1.util"
LOGGING_UTIL = "flat_test_project_1.logging_util"
EXPORTER = "flat_test_project_1.exporter"
RUNTIME = "flat_test_project_1.runtime"
ORCHESTRATION = "flat_test_project_1.orchestration"
SERVICES = "flat_test_project_1.services"
PERSISTENCE = "flat_test_project_1.persistence"


def test_returns_multiple_rule_applier() -> None:
    result = onion_architecture(MODEL, LOGGING_UTIL, EXPORTER)
    assert isinstance(result, MultipleRuleApplier)


def test_valid_onion_architecture_passes(flat_project_1: EvaluableArchitecture) -> None:
    # model (domain) imports nothing - valid
    # persistence (application) imports model and util - util is outside the three layers, so only model is checked
    # exporter (infrastructure) imports logging_util, model, util - but only logging_util is application, model is domain
    # This passes because infrastructure may access both domain and application
    onion_architecture(MODEL, PERSISTENCE, EXPORTER).assert_applies(flat_project_1)


def test_domain_accessing_application_violates_onion(
    flat_project_1: EvaluableArchitecture,
) -> None:
    # logging_util imports util - if we declare util as application and logging_util as domain,
    # then domain (logging_util) accesses application (util), which violates onion rules
    with pytest.raises(AssertionError):
        onion_architecture(LOGGING_UTIL, UTIL, EXPORTER).assert_applies(flat_project_1)


def test_application_accessing_infrastructure_violates_onion(
    flat_project_1: EvaluableArchitecture,
) -> None:
    # services imports persistence - if persistence is infrastructure and services is application,
    # then application accesses infrastructure, which violates onion rules
    with pytest.raises(AssertionError):
        onion_architecture(MODEL, SERVICES, PERSISTENCE).assert_applies(flat_project_1)
