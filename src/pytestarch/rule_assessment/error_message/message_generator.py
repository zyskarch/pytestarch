"""Converts a RuleViolations object into a human-readable format."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from typing import cast

from pytestarch.eval_structure.evaluable_architecture import (
    Dependency,
    Layer,
    LayerMapping,
    Module,
)
from pytestarch.rule_assessment.rule_check.rule_violations import RuleViolations

LAYER_FIRST_LETTER = "l"
LAYER_FIRST_LETTER_CAPITAL = "L"

IMPORT = "import"
IMPORTED_BY = "imported by"

THIRD_PERSON_SINGULAR = "s"

RULE_OBJECT_IS_SUBMODULE_MARKER = "a sub module of "
ANY_MODULE_THAT_IS_NOT = "any module that is not "
ANY_LAYER_THAT_IS_NOT = "any layer that is not "


@dataclass
class RuleViolatedMessage:
    rule_subject: str
    rule_verb: str
    rule_object: str


# (Import, negated, subject singular)
PREFIX_MAPPING: defaultdict[tuple[bool, bool, bool], str] = defaultdict(str)
PREFIX_MAPPING.update(
    {
        (False, False, True): "is ",
        (False, True, True): "is not ",
        (True, True, True): "does not ",
        (False, False, False): "are ",
        (False, True, False): "are not ",
        (True, True, False): "do not ",
    }
)


class RuleViolationMessageBaseGenerator(ABC):
    def create_rule_violation_message(self, rule_violations: RuleViolations) -> str:
        return "\n".join(self.create_rule_violation_messages(rule_violations))

    def create_rule_violation_messages(
        self, rule_violations: RuleViolations
    ) -> list[str]:
        """Create a message about each rule violation.

        Args:
            rule_violations: to convert to human-readable format

        Returns:
            set of messages, each representing a rule violation
        """
        messages = set()
        for message in self._create_violation_messages(rule_violations):
            messages.add(
                f"{message.rule_subject} {message.rule_verb} {message.rule_object}."
            )

        return sorted(list(messages))

    def _create_violation_messages(
        self, rule_violations: RuleViolations
    ) -> list[RuleViolatedMessage]:
        messages: list[RuleViolatedMessage] = []

        self._extend(
            messages, self._create_should_import_violated_messages(rule_violations)
        )
        self._extend(
            messages, self._create_should_only_import_violated_messages(rule_violations)
        )
        self._extend(
            messages, self._create_should_not_import_violated_messages(rule_violations)
        )
        self._extend(
            messages,
            self._create_should_import_except_violated_messages(rule_violations),
        )
        self._extend(
            messages,
            self._create_should_only_import_except_violated_messages(rule_violations),
        )
        self._extend(
            messages,
            self._create_should_not_import_except_violated_messages(rule_violations),
        )

        return messages

    def _extend(
        self,
        messages: list[RuleViolatedMessage],
        new_messages: list[RuleViolatedMessage] | None,
    ) -> None:
        if new_messages is not None:
            messages.extend(new_messages)

    @abstractmethod
    def _create_should_import_violated_messages(
        self, rule_violations: RuleViolations
    ) -> list[RuleViolatedMessage]:
        pass

    @abstractmethod
    def _create_should_only_import_violated_messages(
        self, rule_violations: RuleViolations
    ) -> list[RuleViolatedMessage]:
        pass

    @abstractmethod
    def _create_should_not_import_violated_messages(
        self, rule_violations: RuleViolations
    ) -> list[RuleViolatedMessage]:
        pass

    @abstractmethod
    def _create_should_import_except_violated_messages(
        self, rule_violations: RuleViolations
    ) -> list[RuleViolatedMessage]:
        pass

    @abstractmethod
    def _create_should_only_import_except_violated_messages(
        self, rule_violations: RuleViolations
    ) -> list[RuleViolatedMessage]:
        pass

    @abstractmethod
    def _create_should_not_import_except_violated_messages(
        self, rule_violations: RuleViolations
    ) -> list[RuleViolatedMessage]:
        pass


class RuleViolationMessageGenerator(RuleViolationMessageBaseGenerator):
    """Generates a user-friendly error message for each violated rule defined on modules (as compared to layers)."""

    def __init__(self, import_rule: bool) -> None:
        """
        Args:
            import_rule: True if the underlying rule is an "import" instead of an "is imported" rule
        """
        self._import_rule = import_rule

        self._base_verb = IMPORT if self._import_rule else IMPORTED_BY

    def _create_should_import_violated_messages(
        self, rule_violations: RuleViolations
    ) -> list[RuleViolatedMessage]:
        return self._create_no_import_between_original_subject_and_objects_message(
            rule_violations.should_violations
        )

    def _create_no_import_between_original_subject_and_objects_message(
        self, rule_violations: Iterable[Dependency]
    ) -> list[RuleViolatedMessage]:
        messages: list[RuleViolatedMessage] = []

        (
            rule_objects_for_rule_subject,
            violating_rule_subjects,
        ) = self._get_violating_rule_subjects_and_objects(rule_violations)

        for rule_subject in violating_rule_subjects:
            verb_prefix = self._get_verb_prefix(
                negated=True, subject_singular=self._is_singular_module(rule_subject)
            )
            rule_verb = self._concatenate_verb(prefix=verb_prefix, verb=self._base_verb)

            rule_objects = []
            for rule_object in rule_objects_for_rule_subject[rule_subject]:
                rule_objects.append(self._get_rule_object(rule_object))

            rule_objects.sort()

            rule_subject_formatted = self._get_rule_subject_formatted(rule_subject)
            self._add_combined_rule_objects(
                messages, rule_objects, rule_subject_formatted, rule_verb
            )

        return messages

    def _add_combined_rule_objects(
        self,
        messages: list[RuleViolatedMessage],
        rule_objects: list[str],
        rule_subject: str,
        rule_verb: str,
    ) -> None:
        combined_rule_object = ", ".join(rule_objects)
        if combined_rule_object:
            messages.append(
                RuleViolatedMessage(rule_subject, rule_verb, combined_rule_object)
            )

    def _get_violating_rule_subjects_and_objects(
        self, rule_violation_dependencies: Iterable[Dependency]
    ) -> tuple[dict[Module, list[Module]], set[Module]]:
        violating_rule_subjects = set()
        rule_objects_for_rule_subject = defaultdict(list)
        for rule_subject, rule_object in rule_violation_dependencies:
            violating_rule_subjects.add(rule_subject)
            rule_objects_for_rule_subject[rule_subject].append(rule_object)

        return rule_objects_for_rule_subject, violating_rule_subjects

    def _convert_to_names(
        self, violating_dependencies: list[Dependency]
    ) -> list[tuple[str, str]]:
        return [
            (dependency[0].identifier, dependency[1].identifier)
            for dependency in violating_dependencies
        ]

    def _create_should_only_import_violated_messages(
        self, rule_violations: RuleViolations
    ) -> list[RuleViolatedMessage]:
        messages: list[RuleViolatedMessage] = []

        self._extend(
            messages,
            self._create_should_only_import_forbidden_import_violated_messages(
                rule_violations
            ),
        )
        self._extend(
            messages,
            self._create_should_only_import_no_import_violated_messages(
                rule_violations
            ),
        )

        return messages

    def _create_should_only_import_forbidden_import_violated_messages(
        self, rule_violations: RuleViolations
    ) -> list[RuleViolatedMessage]:
        return self._create_other_violating_dependencies_message(
            rule_violations.should_only_violations_by_forbidden_import
        )

    def _create_other_violating_dependencies_message(
        self,
        violating_dependencies: Iterable[Dependency],
    ) -> list[RuleViolatedMessage]:
        # messages are always of the type "module x imports module y"
        messages = []

        verb_prefix = self._get_verb_prefix(negated=False, subject_singular=True)
        suffix = self._get_verb_suffix(subject_singular=True)
        rule_verb = self._concatenate_verb(
            prefix=verb_prefix, verb=self._base_verb, suffix=suffix
        )

        for dependency in violating_dependencies:
            (
                rule_subject,
                rule_object,
            ) = self._get_rule_subject_and_object_of_dependency(dependency)
            messages.append(RuleViolatedMessage(rule_subject, rule_verb, rule_object))

        messages.sort(key=lambda m: (m.rule_subject, m.rule_object))

        return messages

    def _create_should_only_import_no_import_violated_messages(
        self, rule_violations: RuleViolations
    ) -> list[RuleViolatedMessage]:
        return self._create_no_import_between_original_subject_and_objects_message(
            rule_violations.should_only_violations_by_no_import
        )

    def _create_should_not_import_violated_messages(
        self, rule_violations: RuleViolations
    ) -> list[RuleViolatedMessage]:
        return self._create_other_violating_dependencies_message(
            rule_violations.should_not_violations
        )

    def _create_should_import_except_violated_messages(
        self, rule_violations: RuleViolations
    ) -> list[RuleViolatedMessage]:
        return self._create_no_import_other_than_between_original_subject_and_objects_message(
            rule_violations.should_except_violations
        )

    def _create_no_import_other_than_between_original_subject_and_objects_message(
        self, rule_violations: Iterable[Dependency]
    ) -> list[RuleViolatedMessage]:
        messages: list[RuleViolatedMessage] = []

        (
            rule_objects_for_rule_subject,
            violating_rule_subjects,
        ) = self._get_violating_rule_subjects_and_objects(rule_violations)

        for rule_subject in violating_rule_subjects:
            verb_prefix = self._get_verb_prefix(
                negated=True, subject_singular=self._is_singular_module(rule_subject)
            )
            rule_verb = self._concatenate_verb(prefix=verb_prefix, verb=self._base_verb)

            rule_objects = []
            for rule_object in rule_objects_for_rule_subject[rule_subject]:
                rule_objects.append(
                    self._get_rule_object(rule_object),
                )

            rule_objects.sort()

            rule_subject_formatted = self._get_rule_subject_formatted(rule_subject)
            self._add_combined_any_rule_objects(
                messages, rule_objects, rule_subject_formatted, rule_verb
            )

        return messages

    def _add_combined_any_rule_objects(
        self,
        messages: list[RuleViolatedMessage],
        rule_objects: list[str],
        rule_subject: str,
        rule_verb: str,
        rule_object_type: str = ANY_MODULE_THAT_IS_NOT,
    ) -> None:
        if rule_objects:
            combined_rule_object = rule_object_type + ", ".join(rule_objects)

            messages.append(
                RuleViolatedMessage(rule_subject, rule_verb, combined_rule_object)
            )

    def _create_should_only_import_except_violated_messages(
        self, rule_violations: RuleViolations
    ) -> list[RuleViolatedMessage]:
        messages: list[RuleViolatedMessage] = []

        self._extend(
            messages,
            self._create_should_only_import_except_forbidden_import_violated_messages(
                rule_violations
            ),
        )
        self._extend(
            messages,
            self._create_should_only_import_except_no_import_violated_messages(
                rule_violations
            ),
        )

        return messages

    def _create_should_only_import_except_forbidden_import_violated_messages(
        self, rule_violations: RuleViolations
    ) -> list[RuleViolatedMessage]:
        return self._create_other_violating_dependencies_message(
            rule_violations.should_only_except_violations_by_forbidden_import
        )

    def _create_should_only_import_except_no_import_violated_messages(
        self, rule_violations: RuleViolations
    ) -> list[RuleViolatedMessage]:
        return self._create_no_import_other_than_between_original_subject_and_objects_message(
            rule_violations.should_only_except_violations_by_no_import
        )

    def _create_should_not_import_except_violated_messages(
        self, rule_violations: RuleViolations
    ) -> list[RuleViolatedMessage]:
        return self._create_other_violating_dependencies_message(
            rule_violations.should_not_except_violations
        )

    def _get_module_name(self, module: Module) -> str:
        return module.identifier

    def _is_singular_module(self, module: Module) -> bool:
        return module.is_single_module

    def _get_verb_prefix(self, negated: bool, subject_singular: bool) -> str:
        return PREFIX_MAPPING[(self._import_rule, negated, subject_singular)]  # type: ignore

    def _concatenate_verb(self, verb: str, prefix: str = "", suffix="") -> str:
        return f"{prefix}{verb}{suffix}"

    def _get_rule_object(self, rule_object: Module) -> str:
        module_qualifier = (
            ""
            if self._is_singular_module(rule_object)
            else RULE_OBJECT_IS_SUBMODULE_MARKER
        )
        return f"{module_qualifier}{self._get_quoted_name(self._get_module_name(rule_object))}"

    def _get_rule_subject_formatted(self, rule_subject: Module) -> str:
        prefix = ""
        if not self._is_singular_module(
            rule_subject
        ):  # assumes that all modules here are of the same type
            prefix = "Sub modules of "

        return f'{prefix}"{self._get_module_name(rule_subject)}"'

    def _get_quoted_name(self, name: str) -> str:
        return f'"{name}"'

    def _get_rule_subject_and_object_of_dependency(
        self, dependency: Dependency
    ) -> tuple[str, str]:
        rule_subject_name = self._get_module_name(dependency[0])
        rule_object_name = self._get_module_name(dependency[1])

        rule_subject_name_formatted = self._get_quoted_name(rule_subject_name)
        rule_object_name_formatted = self._get_quoted_name(rule_object_name)

        complete_rule_subject_name = rule_subject_name_formatted + self._get_suffix(
            rule_subject_name
        )
        complete_rule_object_name = rule_object_name_formatted + self._get_suffix(
            rule_object_name
        )
        return complete_rule_subject_name, complete_rule_object_name

    def _get_verb_suffix(self, subject_singular: bool) -> str:
        if not subject_singular:
            return ""

        if self._import_rule:
            return THIRD_PERSON_SINGULAR

        # "is imported by" does not need an additional 's'
        return ""

    def _get_suffix(self, xbject: str) -> str:
        # no suffix needed here
        return ""


class LayerRuleViolationMessageGenerator(RuleViolationMessageGenerator):
    """Generates a user-friendly error message for each violated rule defined on layers (as compared to modules).
    These messages differ slightly from messages generated for rules based on modules:
    1) For absent, but expected dependencies, the verb used mirrors the verb used in the rule itself ("access" instead of "import").
    2) For unwanted dependencies, the regular syntax is used, but with an added hint on which layers the problematic modules
     belong to, such as "module X (layer L) imports module Y (layer M)". If a module does not belong to any layer, (no layer)
     will be used.
    """

    def __init__(self, import_rule: bool, layer_mapping: LayerMapping) -> None:
        super().__init__(import_rule)
        self._layer_mapping = layer_mapping

    def _get_suffix(self, xbject: str) -> str:
        layer = self._layer_mapping.get_layer_for_module_name(xbject)

        if layer is None:
            return " (no layer)"
        else:
            return f" (layer {self._get_quoted_name(layer)})"

    def _create_no_import_between_original_subject_and_objects_message(
        self, rule_violations: Iterable[Dependency]
    ) -> list[RuleViolatedMessage]:
        messages: list[RuleViolatedMessage] = []

        (
            rule_object_layers_for_rule_subject_layer,
            violating_rule_subject_layers,
        ) = self._get_violating_rule_subject_and_objects_layers(rule_violations)

        for rule_subject_layer in violating_rule_subject_layers:
            verb_prefix = self._get_verb_prefix(
                negated=True,
                subject_singular=True,  # only singular rule subjects allowed for layer rules
            )
            rule_verb = self._concatenate_verb(prefix=verb_prefix, verb=self._base_verb)

            rule_object_layers = []
            for rule_object_layer in sorted(
                rule_object_layers_for_rule_subject_layer[rule_subject_layer]
            ):
                rule_object_layer_formatted = self._prepend_prefix(
                    self._get_quoted_name(rule_object_layer), False
                )
                rule_object_layers.append(rule_object_layer_formatted)

            rule_subject_layer_formatted = self._prepend_prefix(
                self._get_quoted_name(rule_subject_layer)
            )
            self._add_combined_rule_objects(
                messages, rule_object_layers, rule_subject_layer_formatted, rule_verb
            )

        return messages

    def _get_violating_rule_subject_and_objects_layers(
        self, rule_violation_dependencies: Iterable[Dependency]
    ) -> tuple[defaultdict[str, set[str]], set[str]]:
        violating_rule_subject_layers = set()
        rule_object_layers_for_rule_subject_layer = defaultdict(set)

        for rule_subject, rule_object in rule_violation_dependencies:
            rule_subject_layer = self._layer_mapping.get_layer_for_module_name(
                rule_subject.identifier
            )
            rule_subject_layer = cast(Layer, rule_subject_layer)
            rule_object_layer = self._layer_mapping.get_layer_for_module_name(
                rule_object.identifier
            )
            rule_object_layer = cast(Layer, rule_object_layer)

            violating_rule_subject_layers.add(rule_subject_layer)
            rule_object_layers_for_rule_subject_layer[rule_subject_layer].add(
                rule_object_layer
            )

        return rule_object_layers_for_rule_subject_layer, violating_rule_subject_layers

    def _create_no_import_other_than_between_original_subject_and_objects_message(
        self, rule_violations: Iterable[Dependency]
    ) -> list[RuleViolatedMessage]:
        messages: list[RuleViolatedMessage] = []

        (
            rule_object_layers_for_rule_subject,
            violating_rule_subject_layers,
        ) = self._get_violating_rule_subject_and_objects_layers(rule_violations)

        for rule_subject_layer in violating_rule_subject_layers:
            verb_prefix = self._get_verb_prefix(
                negated=True,
                subject_singular=True,  # only singular rule subjects allowed for layer rules
            )
            rule_verb = self._concatenate_verb(prefix=verb_prefix, verb=self._base_verb)

            rule_objects = []
            for rule_object_layer in sorted(
                rule_object_layers_for_rule_subject[rule_subject_layer]
            ):
                rule_object_layer_formatted = self._prepend_prefix(
                    self._get_quoted_name(rule_object_layer), False
                )
                rule_objects.append(rule_object_layer_formatted)

            rule_subject_layer_formatted = self._prepend_prefix(
                self._get_quoted_name(rule_subject_layer)
            )
            self._add_combined_any_rule_objects(
                messages,
                rule_objects,
                rule_subject_layer_formatted,
                rule_verb,
                rule_object_type=ANY_LAYER_THAT_IS_NOT,
            )

        return messages

    def _prepend_prefix(self, xbject: str, capital: bool = True) -> str:
        first_letter = LAYER_FIRST_LETTER_CAPITAL

        if not capital:
            first_letter = LAYER_FIRST_LETTER

        return f"{first_letter}ayer {xbject}"
