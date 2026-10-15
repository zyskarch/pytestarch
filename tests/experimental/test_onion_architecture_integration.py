from __future__ import annotations

import pytest

from pytestarch import EvaluableArchitecture
from pytestarch.experimental import onion_architecture

MODEL = "flat_test_project_1.model"
EXPORTER = "flat_test_project_1.exporter"
IMPORTER = "flat_test_project_1.importer"
PERSISTENCE = "flat_test_project_1.persistence"
ORCHESTRATION = "flat_test_project_1.orchestration"
SERVICES = "flat_test_project_1.services"
SIMULATION = "flat_test_project_1.simulation"
RUNTIME = "flat_test_project_1.runtime"


def test_expected_onion_architecture_applies(flat_project_1: EvaluableArchitecture):
    """Based on the dependency structure of flat_test_project_1:

        - orchestration, services (application services) import
          importer, exporter, simulation, persistence (domain services) and
          model (domain model)
        - runtime (adapter) imports orchestration, services

    Unmapped modules 'logging_util' and 'util' are not part of the onion
    architecture and therefore not restricted in any way.
    """
    (
        onion_architecture()
        .domain_models(MODEL)
        .domain_services([IMPORTER, EXPORTER, SIMULATION, PERSISTENCE])
        .application_services([ORCHESTRATION, SERVICES])
        .adapter("cli", RUNTIME)
    ).assert_applies(flat_project_1)


def test_violating_onion_architecture_raises_error_message(
    flat_project_1: EvaluableArchitecture,
):
    model = "flat_test_project_1.model.model_importee"

    onion = onion_architecture().domain_models(MODEL).adapter("cli", PERSISTENCE)

    with pytest.raises(AssertionError) as error:
        onion.assert_applies(flat_project_1)

    message = str(error.value)

    # model is accessed by exporter, importer and simulation, none of which is
    # part of the (nearly empty) onion architecture; each violation is reported
    # via the concrete importing file module
    violating_importers = {
        EXPORTER: f"{EXPORTER}.exporter_importer",
        IMPORTER: f"{IMPORTER}.importer_importer",
        SIMULATION: f"{SIMULATION}.simulation_importer",
    }
    for package, importing_file in violating_importers.items():
        expected_violation = (
            f'"{model}" (layer "domain model") is imported by "{importing_file}"'
            " (no layer)."
        )
        assert expected_violation in message


def test_adapter_accessed_by_another_layer_raises_error(
    flat_project_1: EvaluableArchitecture,
):
    """The cli adapter 'exporter' is accessed by the application service
    'orchestration', which is not allowed. The rest adapter 'runtime' may
    access the application service, though.
    """
    onion = (
        onion_architecture()
        .application_services(ORCHESTRATION)
        .adapter("cli", EXPORTER)
        .adapter("rest", RUNTIME)
    )

    with pytest.raises(AssertionError) as error:
        onion.assert_applies(flat_project_1)

    message = str(error.value)

    assert message.startswith(f"{onion} was violated:\n")
    assert (
        f'"{EXPORTER}.exporter_importee" (layer "cli adapter") is imported by '
        f'"{ORCHESTRATION}.orchestration_importer" (layer "application service").'
    ) in message


def test_application_service_accessed_by_outside_module_raises_error(
    flat_project_1: EvaluableArchitecture,
):
    """The only module accessing the application service 'orchestration' is
    'runtime', which is not part of the onion architecture here and therefore
    not allowed to access it.
    """
    onion = onion_architecture().application_services(ORCHESTRATION)

    with pytest.raises(AssertionError) as error:
        onion.assert_applies(flat_project_1)

    message = str(error.value)

    assert message.startswith(f"{onion} was violated:\n")
    assert (
        f'"{ORCHESTRATION}.orchestration_importee" (layer "application service")'
        f' is imported by "{RUNTIME}.runtime_importer" (no layer).'
    ) in message
