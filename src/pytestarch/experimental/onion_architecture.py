"""Draft of a predefined 'Onion Architecture' rule, inspired by ArchUnit's
`Architectures.onionArchitecture() <https://www.archunit.org/userguide/html/000_Index.html#_onion_architecture>`_.
It is implemented as a convenience wrapper around the layer rule syntax defined
by :class:`pytestarch.LayeredArchitecture` and :class:`pytestarch.LayerRule`.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import cast

from pytestarch import EvaluableArchitecture, LayeredArchitecture, LayerRule
from pytestarch.experimental._utils import assert_applies_with_violation_summary
from pytestarch.query_language.base_language import (
    BaseLayeredArchitecture,
    RuleApplier,
)
from pytestarch.query_language.exceptions import ImproperlyConfigured
from pytestarch.query_language.multiple_rule_applier import MultipleRuleApplier
from pytestarch.utils.list_helpers import listify

DOMAIN_MODEL_LAYER = "domain model"
DOMAIN_SERVICE_LAYER = "domain service"
APPLICATION_SERVICE_LAYER = "application service"
ADAPTER_LAYER_SUFFIX = "adapter"

_MISSING_CONFIGURATION_ERROR_MESSAGE = (
    "Specify at least one component of the onion architecture first: domain"
    " models, domain services, application services, or adapter."
)


def onion_architecture() -> OnionArchitecture:
    """Entry point to a predefined Onion Architecture rule, mirroring the
    structure of ArchUnit's onionArchitecture() builder.

    Returns:
        OnionArchitecture builder, to be configured via its domain_models,
        domain_services, application_services, and adapter methods.
    """
    return OnionArchitecture()


class OnionArchitecture:
    """Predefined rule assessing whether an evaluable architecture complies with
    the Onion Architecture style: adapters access application services, which
    access domain services, which access domain models. Only these components
    may access the domain models, only adapters and application services may
    access the domain services, and only adapters may access the application
    services. Conversely, adapters must not be accessed by anyone.

    Each component is defined via the methods of this class; multiple modules
    belonging to the same component can be specified at once. The resulting
    rules are then applied to an evaluable architecture via 'assert_applies'.

    Note that this does not restrict which modules a component itself imports -
    only who is allowed to access a given component. Also note that
    dependencies between modules of the same component are always allowed.

    Misconfigurations - a component specified more than once, a component
    without modules, or a module assigned to more than one component - are
    rejected with an ImproperlyConfigured error as soon as they are specified.
    Modules nested under or above a module of another component are rejected
    with the same error when the equivalent layered architecture is built.

    Example:
        onion_architecture()
        .domain_models("my_project.domain.model")
        .domain_services("my_project.domain.service")
        .application_services("my_project.application")
        .adapter("cli", "my_project.adapter.cli")
        .assert_applies(evaluable)
    """

    def __init__(self) -> None:
        self._domain_models: list[str] | None = None
        self._domain_services: list[str] | None = None
        self._application_services: list[str] | None = None
        self._adapters: dict[str, list[str]] = {}

    def domain_models(self, modules: str | Sequence[str]) -> OnionArchitecture:
        """Defines which modules make up the domain models, the innermost
        layer of the architecture.

        Args:
            modules: module or list of modules belonging to the domain models.

        Raises:
            ImproperlyConfigured: if the domain models are specified more than
                once, no modules are given, or a module already belongs to
                another component.
        """
        self._domain_models = self._set_component(
            "domain models", self._domain_models, modules
        )
        return self

    def domain_services(self, modules: str | Sequence[str]) -> OnionArchitecture:
        """Defines which modules make up the domain services, which may access
        the domain models.

        Args:
            modules: module or list of modules belonging to the domain services.

        Raises:
            ImproperlyConfigured: if the domain services are specified more
                than once, no modules are given, or a module already belongs to
                another component.
        """
        self._domain_services = self._set_component(
            "domain services", self._domain_services, modules
        )
        return self

    def application_services(self, modules: str | Sequence[str]) -> OnionArchitecture:
        """Defines which modules make up the application services, which may
        access the domain services and the domain models.

        Args:
            modules: module or list of modules belonging to the application services.

        Raises:
            ImproperlyConfigured: if the application services are specified
                more than once, no modules are given, or a module already
                belongs to another component.
        """
        self._application_services = self._set_component(
            "application services", self._application_services, modules
        )
        return self

    def adapter(self, name: str, modules: str | Sequence[str]) -> OnionArchitecture:
        """Defines which modules make up an adapter of the given name, which
        may access all other components but must not be accessed itself.

        Args:
            name: name of the adapter, e.g. 'cli'. Must be unique.
            modules: module or list of modules belonging to the adapter.

        Raises:
            ImproperlyConfigured: if an adapter of the given name already
                exists, no modules are given, or a module already belongs to
                another component.
        """
        if name in self._adapters:
            raise ImproperlyConfigured(f"Adapter {name} already exists.")

        self._adapters[name] = self._validated_modules(f"adapter {name}", modules)
        return self

    def layered_architecture(self) -> LayeredArchitecture:
        """Converts this rule into the equivalent layered architecture. Each
        component maps to one layer. This is the basis of all rules applied by
        'assert_applies' and can also be used to define additional layer rules
        on top of the onion architecture.

        Returns:
            LayeredArchitecture with one layer each for the domain models, the
            domain services, the application services, and each adapter.

        Raises:
            ImproperlyConfigured: if no component has been specified.
        """
        self._assert_at_least_one_component_specified()

        arch: BaseLayeredArchitecture = LayeredArchitecture()

        for layer_name, modules in self._layer_definitions():
            if modules is not None:
                arch = arch.with_layer().layer(layer_name).containing_modules(modules)

        return cast(LayeredArchitecture, arch)

    def assert_applies(self, evaluable: EvaluableArchitecture) -> None:
        """Applies this architecture's rules to the given evaluable. One layer
        rule per component is derived from the component structure according to
        the Onion Architecture style, e.g. 'domain model may only be accessed
        by the domain services, application services, and adapters'.

        Args:
            evaluable: module dependency structure to compare the rules against.

        Raises:
            ImproperlyConfigured: if no component has been specified.
            AssertionError: with an aggregated error message if this
                architecture is violated by the evaluable. The message is
                prefixed with a description of the violated architecture.
        """
        arch = self.layered_architecture()
        adapter_layer_names = self._adapter_layer_names()

        allowed_accessors_by_layer = {
            DOMAIN_MODEL_LAYER: [
                DOMAIN_SERVICE_LAYER,
                APPLICATION_SERVICE_LAYER,
                *adapter_layer_names,
            ],
            DOMAIN_SERVICE_LAYER: [
                APPLICATION_SERVICE_LAYER,
                *adapter_layer_names,
            ],
            APPLICATION_SERVICE_LAYER: list(adapter_layer_names),
        }

        rules: list[RuleApplier] = []

        for layer, modules in self._core_layer_definitions():
            if modules is None:
                continue

            rules.append(
                self._accessibility_rule(
                    arch,
                    layer,
                    self._specified_layers(allowed_accessors_by_layer[layer]),
                )
            )

        for adapter_layer_name in adapter_layer_names:
            # an adapter may not be accessed by any layer
            rules.append(self._accessibility_rule(arch, adapter_layer_name, []))

        assert_applies_with_violation_summary(
            MultipleRuleApplier(rules).assert_applies, evaluable, self
        )

    def __str__(self) -> str:
        components = [
            f"{DOMAIN_MODEL_LAYER}: {self._format(self._domain_models)}",
            f"{DOMAIN_SERVICE_LAYER}: {self._format(self._domain_services)}",
            f"{APPLICATION_SERVICE_LAYER}: {self._format(self._application_services)}",
        ] + [
            f"adapter '{name}': {self._format(modules)}"
            for name, modules in self._adapters.items()
        ]

        return "Onion Architecture: " + "; ".join(components)

    @staticmethod
    def _format(modules: list[str] | None) -> str:
        if modules is None:
            return "not specified"

        return f"[{', '.join(modules)}]"

    def _layer_definitions(self) -> list[tuple[str, list[str] | None]]:
        """Returns the layer name and modules of every component of this
        architecture, with the modules of unspecified components being None.
        """
        return [
            *self._core_layer_definitions(),
            *[
                (self._adapter_layer_name(name), modules)
                for name, modules in self._adapters.items()
            ],
        ]

    def _core_layer_definitions(self) -> list[tuple[str, list[str] | None]]:
        return [
            (DOMAIN_MODEL_LAYER, self._domain_models),
            (DOMAIN_SERVICE_LAYER, self._domain_services),
            (APPLICATION_SERVICE_LAYER, self._application_services),
        ]

    @staticmethod
    def _adapter_layer_name(adapter_name: str) -> str:
        return f"{adapter_name} {ADAPTER_LAYER_SUFFIX}"

    def _specified_layers(self, layer_names: list[str]) -> list[str]:
        """Returns the subset of the given layer names whose component has been
        specified. Unspecified components do not contribute any modules, so
        restricting access to them would split the whitelist.
        """
        specified_layer_names = {
            layer_name
            for layer_name, modules in self._layer_definitions()
            if modules is not None
        }

        return [
            layer_name
            for layer_name in layer_names
            if layer_name in specified_layer_names
        ]

    def _adapter_layer_names(self) -> list[str]:
        return [self._adapter_layer_name(name) for name in self._adapters]

    def _accessibility_rule(
        self, arch: LayeredArchitecture, layer: str, allowed_accessors: list[str]
    ) -> RuleApplier:
        """Creates a rule stating that the given layer may only be accessed by
        the given layers. If there are no allowed accessors, all access to the
        layer is forbidden instead.

        Args:
            arch: layered architecture containing the layer definitions.
            layer: name of the layer to restrict access to.
            allowed_accessors: names of the layers that may access this layer.

        Returns:
            Rule of the form 'layer X should not be accessed by layers except
            [Y, Z]' or, if there are no allowed accessors, 'layer X should not
            be accessed by any layer'.
        """
        rule = LayerRule().based_on(arch).layers_that().are_named(layer).should_not()

        if allowed_accessors:
            return rule.be_accessed_by_layers_except_layers_that().are_named(
                allowed_accessors
            )

        return rule.be_accessed_by_any_layer()

    def _set_component(
        self,
        component: str,
        current_modules: list[str] | None,
        modules: str | Sequence[str],
    ) -> list[str]:
        """Sets the modules of one of the core components of this architecture.

        Args:
            component: name of the component, used in error messages.
            current_modules: modules currently assigned to the component, if any.
            modules: module or list of modules belonging to the component.

        Returns:
            the component's validated modules.

        Raises:
            ImproperlyConfigured: if the component is already specified or the
                modules are invalid.
        """
        self._assert_not_yet_specified(component, current_modules)
        return self._validated_modules(component, modules)

    def _validated_modules(
        self, component: str, modules: str | Sequence[str]
    ) -> list[str]:
        """Converts the given modules into a list, asserting that no modules
        are missing and that none of them already belongs to another component.
        Nesting between components is not checked here: modules nested under or
        above a module of another component are rejected when the equivalent
        layered architecture is built.

        Args:
            component: name of the component the modules belong to, used in
                error messages.
            modules: module or list of modules belonging to the component.

        Returns:
            the modules as a list.

        Raises:
            ImproperlyConfigured: if no modules are given or a module is
                already assigned to a component of this architecture.
        """
        modules = listify(modules)

        if not modules:
            raise ImproperlyConfigured(
                f"The {component} of the onion architecture must contain at least"
                " one module."
            )

        duplicates = self._assigned_modules().intersection(modules)

        if duplicates:
            raise ImproperlyConfigured(
                f"Module(s) {', '.join(sorted(duplicates))} already assigned to a"
                " layer."
            )

        return modules

    def _assigned_modules(self) -> set[str]:
        """Returns all modules that already belong to a component."""
        return {
            module
            for _, modules in self._layer_definitions()
            if modules is not None
            for module in modules
        }

    @staticmethod
    def _assert_not_yet_specified(component: str, modules: list[str] | None) -> None:
        if modules is not None:
            raise ImproperlyConfigured(
                f"The {component} of the onion architecture are already specified."
            )

    def _assert_at_least_one_component_specified(self) -> None:
        if not any(
            [
                self._domain_models is not None,
                self._domain_services is not None,
                self._application_services is not None,
                self._adapters,
            ]
        ):
            raise ImproperlyConfigured(_MISSING_CONFIGURATION_ERROR_MESSAGE)
