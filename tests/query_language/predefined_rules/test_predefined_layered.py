from __future__ import annotations

import pytest

from pytestarch import EvaluableArchitecture, layered_architecture
from pytestarch.query_language.exceptions import ImproperlyConfigured
from pytestarch.query_language.multiple_rule_applier import MultipleRuleApplier

# Fully-qualified module names from flat_test_project_1
MODEL = "flat_test_project_1.model"
UTIL = "flat_test_project_1.util"
EXPORTER = "flat_test_project_1.exporter"
LOGGING_UTIL = "flat_test_project_1.logging_util"
SERVICES = "flat_test_project_1.services"
IMPORTER = "flat_test_project_1.importer"
PERSISTENCE = "flat_test_project_1.persistence"
RUNTIME = "flat_test_project_1.runtime"
ORCHESTRATION = "flat_test_project_1.orchestration"


def test_returns_multiple_rule_applier(flat_project_1: EvaluableArchitecture) -> None:
    result = layered_architecture(
        layers={"model": MODEL},
        allowed_dependencies={"model": []},
    )
    assert isinstance(result, MultipleRuleApplier)


def test_layer_with_no_allowed_dependencies_passes_when_no_imports(
    flat_project_1: EvaluableArchitecture,
) -> None:
    # model imports nothing - satisfies no-access rule
    layered_architecture(
        layers={"model": MODEL},
        allowed_dependencies={"model": []},
    ).assert_applies(flat_project_1)


def test_layer_with_allowed_dependency_passes_when_only_those_imports(
    flat_project_1: EvaluableArchitecture,
) -> None:
    # logging_util only imports util - satisfies should_only access util
    layered_architecture(
        layers={"logging_util": LOGGING_UTIL, "util": UTIL},
        allowed_dependencies={"logging_util": ["util"]},
    ).assert_applies(flat_project_1)


def test_multiple_allowed_dependencies_passes(
    flat_project_1: EvaluableArchitecture,
) -> None:
    # exporter imports logging_util, model, util - exactly those three
    layered_architecture(
        layers={
            "exporter": EXPORTER,
            "logging_util": LOGGING_UTIL,
            "model": MODEL,
            "util": UTIL,
        },
        allowed_dependencies={
            "exporter": ["logging_util", "model", "util"],
        },
    ).assert_applies(flat_project_1)


def test_empty_allowed_dependencies_raises_when_layer_has_imports(
    flat_project_1: EvaluableArchitecture,
) -> None:
    # exporter imports other modules, so [] should fail
    with pytest.raises(AssertionError):
        layered_architecture(
            layers={"exporter": EXPORTER, "util": UTIL},
            allowed_dependencies={"exporter": []},
        ).assert_applies(flat_project_1)


def test_wrong_allowed_dependency_raises(
    flat_project_1: EvaluableArchitecture,
) -> None:
    # exporter imports logging_util, model, util - specifying only model should fail
    with pytest.raises(AssertionError):
        layered_architecture(
            layers={"exporter": EXPORTER, "model": MODEL},
            allowed_dependencies={"exporter": ["model"]},
        ).assert_applies(flat_project_1)


def test_multiple_violated_rules_aggregates_errors(
    flat_project_1: EvaluableArchitecture,
) -> None:
    # Both exporter and logging_util import other things - both rules fail
    with pytest.raises(AssertionError) as exc_info:
        layered_architecture(
            layers={
                "exporter": EXPORTER,
                "logging_util": LOGGING_UTIL,
                "util": UTIL,
            },
            allowed_dependencies={
                "exporter": [],
                "logging_util": [],
            },
        ).assert_applies(flat_project_1)

    # MultipleRuleApplier joins errors with newline - two separate error messages
    assert "\n" in exc_info.value.args[0]


def test_empty_allowed_dependencies_dict_passes(
    flat_project_1: EvaluableArchitecture,
) -> None:
    # No rules means nothing to violate
    layered_architecture(
        layers={"model": MODEL, "util": UTIL},
        allowed_dependencies={},
    ).assert_applies(flat_project_1)


def test_unknown_subject_in_allowed_dependencies_raises() -> None:
    with pytest.raises(ImproperlyConfigured, match="nonexistent"):
        layered_architecture(
            layers={"model": MODEL},
            allowed_dependencies={"nonexistent": []},
        )


def test_unknown_target_in_allowed_dependencies_raises() -> None:
    with pytest.raises(ImproperlyConfigured, match="nonexistent"):
        layered_architecture(
            layers={"model": MODEL},
            allowed_dependencies={"model": ["nonexistent"]},
        )
