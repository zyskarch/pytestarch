from __future__ import annotations

import pytest

from pytestarch import EvaluableArchitecture
from pytestarch.experimental import layered_architecture

MODEL = "flat_test_project_1.model"
EXPORTER = "flat_test_project_1.exporter"
IMPORTER = "flat_test_project_1.importer"
PERSISTENCE = "flat_test_project_1.persistence"
ORCHESTRATION = "flat_test_project_1.orchestration"
SERVICES = "flat_test_project_1.services"
SIMULATION = "flat_test_project_1.simulation"
RUNTIME = "flat_test_project_1.runtime"
LOGGING_UTIL = "flat_test_project_1.logging_util"
UTIL = "flat_test_project_1.util"


def test_expected_layered_architecture_applies(flat_project_1: EvaluableArchitecture):
    """Based on the dependency structure of flat_test_project_1 (see
    tests/conftest.py):

        - runtime (presentation) imports orchestration, services (application)
        - orchestration, services import importer, exporter, persistence,
          simulation (domain)
        - application and domain import model and logging_util/util
          (cross-cutting)
        - model imports nothing, cross_cutting is unrestricted
    """
    rules = layered_architecture(
        layers={
            "model": MODEL,
            "domain": [IMPORTER, EXPORTER, SIMULATION, PERSISTENCE],
            "application": [ORCHESTRATION, SERVICES],
            "presentation": RUNTIME,
            "cross_cutting": [LOGGING_UTIL, UTIL],
        },
        allowed_dependencies={
            "model": [],
            "domain": ["model", "cross_cutting"],
            "application": ["domain", "model", "cross_cutting"],
            "presentation": ["application", "domain", "cross_cutting"],
        },
    )

    rules.assert_applies(flat_project_1)


def test_violating_layered_architecture_raises_error_message(
    flat_project_1: EvaluableArchitecture,
):
    """The presentation layer is restricted to the application layer, but the
    runtime also imports the domain and cross-cutting layers directly.
    """
    rules = layered_architecture(
        layers={
            "model": MODEL,
            "domain": [IMPORTER, EXPORTER, SIMULATION, PERSISTENCE],
            "application": [ORCHESTRATION, SERVICES],
            "cross_cutting": [LOGGING_UTIL, UTIL],
            "presentation": RUNTIME,
        },
        allowed_dependencies={"presentation": ["application"]},
    )

    with pytest.raises(AssertionError) as error:
        rules.assert_applies(flat_project_1)

    message = str(error.value)

    assert message.startswith(f"{rules} was violated:\n")
    assert (
        f'imports "{PERSISTENCE}.persistence_importee" (layer "domain").'
    ) in message
