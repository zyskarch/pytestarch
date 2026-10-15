"""Draft of a predefined layered architecture rule, inspired by ArchUnit's
`Architectures.layeredArchitecture()
<https://www.archunit.org/userguide/html/000_Index.html#_layered_architecture>`_.
It is implemented as a convenience wrapper around the layer rule syntax defined
by :class:`pytestarch.LayeredArchitecture` and :class:`pytestarch.LayerRule`.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import cast

from pytestarch import EvaluableArchitecture, LayeredArchitecture, LayerRule
from pytestarch.query_language.base_language import (
    BaseLayeredArchitecture,
    RuleApplier,
)
from pytestarch.query_language.exceptions import ImproperlyConfigured
from pytestarch.query_language.multiple_rule_applier import MultipleRuleApplier


def layered_architecture(
    layers: dict[str, str | Sequence[str]],
    allowed_dependencies: dict[str, str | Sequence[str]],
) -> PredefinedLayeredArchitecture:
    """Entry point to a predefined layered architecture rule, mirroring the
    structure of ArchUnit's layeredArchitecture() builder.

    Each entry of 'allowed_dependencies' generates one rule enforcing that the
    named layer may only access the listed layers. An empty list means that the
    layer must not access anything, and layers omitted from
    'allowed_dependencies' are defined but unrestricted.

    Args:
        layers: mapping of layer names to the module or list of modules that
            make up each layer.
        allowed_dependencies: mapping of layer names to the layer name or
            list/sequence of layer names they may access.

    Returns:
        PredefinedLayeredArchitecture rule, to be configured via the given
        mappings and to be applied to an evaluable architecture via
        'assert_applies'.

    Raises:
        ImproperlyConfigured: if no layer is defined in 'layers', if
            'allowed_dependencies' references a layer name that is not defined
            in 'layers' - as subject or as allowed dependency -, a layer's
            module list is empty, a module is already assigned to another
            layer of this architecture, or a module is nested under or is a
            submodule of a module assigned to another layer of this
            architecture. All misconfigurations are detected here, before any
            rule is applied.
    """
    return PredefinedLayeredArchitecture(layers, allowed_dependencies)


class PredefinedLayeredArchitecture(MultipleRuleApplier):
    """Predefined rule assessing whether an evaluable architecture complies with
    the layered architecture defined via the factory function
    'layered_architecture': each layer may only access the layers listed as its
    allowed dependencies.

    Note that this restricts outbound dependencies only - it mirrors the white
    list style of ArchUnit's layer rules, so a layer importing a module that
    belongs to no defined layer is also a violation, while dependencies within
    a layer are always allowed.

    Misconfigurations are rejected with an ImproperlyConfigured error as soon
    as the architecture is constructed: unknown layer names in
    'allowed_dependencies' (as subject or as allowed dependency) and layers
    without modules are detected here, as well as modules assigned to more
    than one layer and modules nested under or above a module of another
    layer.

    Example:
        layered_architecture(
            {
                "controller": "my_project.controller",
                "service": "my_project.service",
                "persistence": "my_project.persistence",
                "model": "my_project.model",
            },
            {"controller": ["service"], "service": ["persistence", "model"]},
        ).assert_applies(evaluable)
    """

    def __init__(
        self,
        layers: dict[str, str | Sequence[str]],
        allowed_dependencies: dict[str, str | Sequence[str]],
    ) -> None:
        self._assert_at_least_one_layer(layers)

        self._modules_by_layer: dict[str, list[str]] = {
            layer_name: self._listify(modules) for layer_name, modules in layers.items()
        }

        normalized_allowed_dependencies: dict[str, list[str]] = {
            layer_name: self._listify(allowed_layers)
            for layer_name, allowed_layers in allowed_dependencies.items()
        }

        self._assert_layers_exist(normalized_allowed_dependencies)
        self._assert_at_least_one_module_per_layer()
        self._assert_module_uniqueness()

        arch: BaseLayeredArchitecture = LayeredArchitecture()

        for layer_name, modules in self._modules_by_layer.items():
            arch = arch.with_layer().layer(layer_name).containing_modules(modules)

        arch = cast(LayeredArchitecture, arch)
        self._layered_architecture = arch

        super().__init__(
            [
                self._accessibility_rule(arch, layer_name, allowed_layers)
                for layer_name, allowed_layers in normalized_allowed_dependencies.items()
            ]
        )

    def layered_architecture(self) -> LayeredArchitecture:
        """Returns the layered architecture of this rule. This is the basis of
        all rules applied by 'assert_applies' and can also be used to define
        additional layer rules on top of the layered architecture.

        Returns:
            LayeredArchitecture with one layer per entry of 'layers'.
        """
        return self._layered_architecture

    def assert_applies(self, evaluable: EvaluableArchitecture) -> None:
        """Applies this architecture's rules to the given evaluable. One layer
        rule per entry of 'allowed_dependencies' is derived from the
        dependency structure, stating that the layer may only access the listed
        layers.

        Args:
            evaluable: module dependency structure to compare the rules against.

        Raises:
            AssertionError: with an aggregated error message if this
                architecture is violated by the evaluable. The message is
                prefixed with a description of the violated architecture.
        """
        try:
            super().assert_applies(evaluable)
        except AssertionError as error:
            # the aggregated violations already contain all information needed
            # to fix the architecture, so suppress the internal traceback to
            # avoid printing the violations twice
            raise AssertionError(f"{self} was violated:\n{error}") from None

    def __str__(self) -> str:
        layers = [
            f"layer '{layer_name}': [{', '.join(modules)}]"
            for layer_name, modules in self._modules_by_layer.items()
        ]

        return "Layered Architecture: " + "; ".join(layers)

    def _assert_at_least_one_layer(
        self, layers: dict[str, str | Sequence[str]]
    ) -> None:
        """Asserts that at least one layer is defined via the 'layers' mapping.

        Raises:
            ImproperlyConfigured: if 'layers' is empty.
        """
        if not layers:
            raise ImproperlyConfigured(
                "Specify at least one layer of the layered architecture first."
            )

    def _assert_layers_exist(self, allowed_dependencies: dict[str, list[str]]) -> None:
        """Asserts that 'allowed_dependencies' only references layers defined
        via the 'layers' mapping, both as subject and as allowed dependency.

        Raises:
            ImproperlyConfigured: if an unknown layer name is referenced.
        """
        unknown_subjects = [
            layer_name
            for layer_name in allowed_dependencies
            if layer_name not in self._modules_by_layer
        ]

        if unknown_subjects:
            raise ImproperlyConfigured(
                f"Layer(s) {', '.join(sorted(unknown_subjects))} referenced in"
                " allowed_dependencies are not defined in layers."
            )

        unknown_dependencies = {
            allowed_layer_name
            for allowed_layers in allowed_dependencies.values()
            for allowed_layer_name in allowed_layers
            if allowed_layer_name not in self._modules_by_layer
        }

        if unknown_dependencies:
            raise ImproperlyConfigured(
                f"Layer(s) {', '.join(sorted(unknown_dependencies))} referenced"
                " as allowed dependencies are not defined in layers."
            )

    def _assert_at_least_one_module_per_layer(self) -> None:
        """Asserts that every layer contains at least one module.

        Raises:
            ImproperlyConfigured: if a layer's module list is empty.
        """
        for layer_name, modules in self._modules_by_layer.items():
            if not modules:
                raise ImproperlyConfigured(
                    f"Layer {layer_name} must contain at least one module."
                )

    def _assert_module_uniqueness(self) -> None:
        """Asserts that no module belongs to more than one layer, so that the
        engine's duplicate error message is never surfaced (whose module order
        depends on hash randomization).

        Raises:
            ImproperlyConfigured: if a module is assigned to more than one layer.
        """
        assigned: set[str] = set()
        duplicates: set[str] = set()
        for modules in self._modules_by_layer.values():
            duplicates.update(assigned.intersection(modules))
            assigned.update(modules)

        if duplicates:
            raise ImproperlyConfigured(
                f"Module(s) {', '.join(sorted(duplicates))} already assigned to a"
                " layer."
            )

    @staticmethod
    def _accessibility_rule(
        arch: LayeredArchitecture, layer: str, allowed_layers: list[str]
    ) -> RuleApplier:
        """Creates a rule stating that the given layer may only access the
        given layers. If there are no allowed dependencies, all outbound
        dependencies are forbidden instead.

        Args:
            arch: layered architecture containing the layer definitions.
            layer: name of the layer whose outbound dependencies are restricted.
            allowed_layers: names of the layers this layer may access.

        Returns:
            LayerRule of the form 'layer X should not access layers except
            [Y, Z]' or, if there are no allowed dependencies, 'layer X should
            not access any layer'.
        """
        rule = LayerRule().based_on(arch).layers_that().are_named(layer).should_not()

        if allowed_layers:
            return rule.access_layers_except_layers_that().are_named(allowed_layers)

        return rule.access_any_layer()

    @staticmethod
    def _listify(modules: str | Sequence[str]) -> list[str]:
        return list(dict.fromkeys([modules] if isinstance(modules, str) else modules))
