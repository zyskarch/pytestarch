from __future__ import annotations

from pytestarch.eval_structure.evaluable_architecture import EvaluableArchitecture
from pytestarch.query_language.base_language import RuleApplier
from pytestarch.query_language.exceptions import ImproperlyConfigured
from pytestarch.query_language.layered_architecture_rule import LayeredArchitecture, LayerRule
from pytestarch.query_language.multiple_rule_applier import MultipleRuleApplier


def layered_architecture(
    layers: dict[str, str | list[str]],
    allowed_dependencies: dict[str, list[str]],
) -> MultipleRuleApplier:
    """Creates rules enforcing a layered architecture.

    Args:
        layers: Mapping from layer name to module name(s).
            E.g. {"presentation": "my_project.presentation", "domain": ["my_project.domain.models", "my_project.domain.services"]}
        allowed_dependencies: Mapping from layer name to list of layer names that layer may access.
            An empty list means the layer must not access any other configured layer.
            E.g. {"presentation": ["application"], "domain": []}

    Returns:
        MultipleRuleApplier that enforces all layer dependency rules.

    Raises:
        ImproperlyConfigured: If allowed_dependencies references layer names not defined in layers.
    """
    unknown_subjects = [name for name in allowed_dependencies if name not in layers]
    if unknown_subjects:
        raise ImproperlyConfigured(
            f"Layer(s) {', '.join(sorted(unknown_subjects))} referenced in allowed_dependencies are not defined in layers."
        )

    unknown_targets: list[str] = []
    for targets in allowed_dependencies.values():
        unknown_targets.extend(name for name in targets if name not in layers)
    if unknown_targets:
        raise ImproperlyConfigured(
            f"Layer(s) {', '.join(sorted(set(unknown_targets)))} referenced as allowed dependencies are not defined in layers."
        )

    arch = LayeredArchitecture()
    for name, modules in layers.items():
        arch.layer(name).containing_modules(modules)

    rules: list[RuleApplier] = []
    for layer_name, allowed in allowed_dependencies.items():
        rule_base = LayerRule().based_on(arch).layers_that().are_named(layer_name)
        if not allowed:
            rule: RuleApplier = rule_base.should_not().access_any_layer()
        else:
            rule = rule_base.should_only().access_layers_that().are_named(allowed)
        rules.append(rule)

    return MultipleRuleApplier(rules)


def onion_architecture(
    domain_layer: str | list[str],
    application_layer: str | list[str],
    infrastructure_layer: str | list[str],
) -> MultipleRuleApplier:
    """Creates rules enforcing an onion architecture.

    The standard onion architecture dependency rules are:
    - Domain layer: may not access application or infrastructure
    - Application layer: may only access domain
    - Infrastructure layer: may access domain and application

    Args:
        domain_layer: Module name(s) for the domain (innermost) layer.
        application_layer: Module name(s) for the application layer.
        infrastructure_layer: Module name(s) for the infrastructure (outermost) layer.

    Returns:
        MultipleRuleApplier that enforces onion architecture dependency rules.
    """
    return layered_architecture(
        layers={
            "domain": domain_layer,
            "application": application_layer,
            "infrastructure": infrastructure_layer,
        },
        allowed_dependencies={
            "domain": [],
            "application": ["domain"],
            "infrastructure": ["domain", "application"],
        },
    )


class HexagonalArchitecture(RuleApplier):
    """Builder for hexagonal (ports and adapters) architecture rules.

    Follows ArchUnit's hexagonal architecture model:
    - Domain models: innermost, no dependencies on other configured layers
    - Domain services: may only access domain models
    - Application services: may only access domain models and domain services
    - Adapters (any number, identified by name): may access domain models, domain services, and application services

    Only layers that are explicitly configured are included in the rule set.

    Example usage::

        HexagonalArchitecture()
            .domain_models("my_project.domain.models")
            .domain_services("my_project.domain.services")
            .application_services("my_project.application")
            .adapter("rest", "my_project.adapters.rest")
            .adapter("db", "my_project.adapters.db")
            .assert_applies(evaluable)
    """

    _DOMAIN_MODELS_LAYER = "domain_models"
    _DOMAIN_SERVICES_LAYER = "domain_services"
    _APPLICATION_SERVICES_LAYER = "application_services"
    _ADAPTER_LAYER_PREFIX = "adapter_"

    def __init__(self) -> None:
        self._layers: dict[str, str | list[str]] = {}

    def domain_models(self, *modules: str) -> HexagonalArchitecture:
        """Configure the domain models layer."""
        self._layers[self._DOMAIN_MODELS_LAYER] = list(modules) if len(modules) > 1 else modules[0]
        return self

    def domain_services(self, *modules: str) -> HexagonalArchitecture:
        """Configure the domain services layer."""
        self._layers[self._DOMAIN_SERVICES_LAYER] = list(modules) if len(modules) > 1 else modules[0]
        return self

    def application_services(self, *modules: str) -> HexagonalArchitecture:
        """Configure the application services layer."""
        self._layers[self._APPLICATION_SERVICES_LAYER] = list(modules) if len(modules) > 1 else modules[0]
        return self

    def adapter(self, name: str, *modules: str) -> HexagonalArchitecture:
        """Configure a named adapter layer (primary or secondary).

        Args:
            name: Unique name for this adapter (e.g. "rest", "db", "cli").
            *modules: Module name(s) that make up this adapter.
        """
        if not modules:
            raise ImproperlyConfigured(f"Adapter '{name}' must have at least one module.")
        layer_key = f"{self._ADAPTER_LAYER_PREFIX}{name}"
        self._layers[layer_key] = list(modules) if len(modules) > 1 else modules[0]
        return self

    def assert_applies(self, evaluable: EvaluableArchitecture) -> None:
        """Check that the architecture rules hold for the given evaluable.

        Raises:
            AssertionError: If one or more architecture rules are violated.
        """
        self._build_rules().assert_applies(evaluable)

    def _build_rules(self) -> MultipleRuleApplier:
        inner_layers = [
            self._DOMAIN_MODELS_LAYER,
            self._DOMAIN_SERVICES_LAYER,
            self._APPLICATION_SERVICES_LAYER,
        ]

        allowed_dependencies: dict[str, list[str]] = {}

        # Each inner layer may only access previously listed inner layers
        for i, layer in enumerate(inner_layers):
            if layer in self._layers:
                allowed_dependencies[layer] = [l for l in inner_layers[:i] if l in self._layers]

        # Each adapter may access all configured inner layers
        configured_inner = [l for l in inner_layers if l in self._layers]
        for layer_key in self._layers:
            if layer_key.startswith(self._ADAPTER_LAYER_PREFIX):
                allowed_dependencies[layer_key] = configured_inner

        return layered_architecture(self._layers, allowed_dependencies)
