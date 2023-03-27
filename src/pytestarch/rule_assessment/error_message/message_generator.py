"""Converts a RuleViolations object into a human-readable format."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from pytestarch.eval_structure.evaluable_architecture import Module, StrictDependency
from pytestarch.rule_assessment.rule_check.rule_violations import RuleViolations

IMPORT = "import"
IMPORTED_BY = "imported by"

THIRD_PERSON_SINGULAR = "s"

RULE_OBJECT_IS_SUBMODULE_MARKER = "a sub module of "
ANY_MODULE_THAT_IS_NOT = "any module that is not "


@dataclass
class RuleViolatedMessage:
    rule_subject: str
    rule_verb: str
    rule_object: str


# (Import, negated, subject singular)
PREFIX_MAPPING = defaultdict(str)
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


class RuleViolationMessageGenerator:
    """Generates a message for each violated rule."""

    def __init__(self, import_rule: bool) -> None:
        """
        Args:
            import_rule: True if the underlying rule is an "import" instead of an "is imported" rule
        """
        self._import_rule = import_rule

        self._base_verb = IMPORT if self._import_rule else IMPORTED_BY

    def create_rule_violation_message(self, rule_violations: RuleViolations) -> str:
        """Create a message about all rule violations.

        Args:
            rule_violations: to convert to human-readable format

        Returns:
            message containing all individual rule violation messages
        """
        return "\n".join(self.create_rule_violation_messages(rule_violations))

    def create_rule_violation_messages(
        self, rule_violations: RuleViolations
    ) -> List[str]:
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
    ) -> List[RuleViolatedMessage]:
        messages = []

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
        messages: List[RuleViolatedMessage],
        new_messages: Optional[List[RuleViolatedMessage]],
    ) -> None:
        if new_messages is not None:
            messages.extend(new_messages)

    def _create_should_import_violated_messages(
        self, rule_violations: RuleViolations
    ) -> List[RuleViolatedMessage]:
        return self._create_no_import_between_original_subject_and_objects_message(
            rule_violations.should_violations
        )

    def _create_no_import_between_original_subject_and_objects_message(
        self, rule_violations: List[StrictDependency]
    ) -> List[RuleViolatedMessage]:
        messages = []

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

            combined_rule_object = ", ".join(rule_objects)
            if combined_rule_object:
                rule_subject_formatted = self._get_rule_subject_formatted(rule_subject)
                messages.append(
                    RuleViolatedMessage(
                        rule_subject_formatted, rule_verb, combined_rule_object
                    )
                )

        return messages

    def _get_violating_rule_subjects_and_objects(
        self, rule_violation_dependency_names: List[StrictDependency]
    ) -> Tuple[Dict[Module, List[Module]], Set[Module]]:
        violating_rule_subjects = set()
        rule_objects_for_rule_subject = defaultdict(list)
        for rule_subject, rule_object in rule_violation_dependency_names:
            violating_rule_subjects.add(rule_subject)
            rule_objects_for_rule_subject[rule_subject].append(rule_object)

        return rule_objects_for_rule_subject, violating_rule_subjects

    def _convert_to_names(
        self, violating_dependencies: List[StrictDependency]
    ) -> List[Tuple[str, str]]:
        return [
            (dependency[0].name, dependency[1].name)
            for dependency in violating_dependencies
        ]

    def _create_should_only_import_violated_messages(
        self, rule_violations: RuleViolations
    ) -> List[RuleViolatedMessage]:
        messages = []

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
    ) -> List[RuleViolatedMessage]:
        return self._create_other_violating_dependencies_message(
            rule_violations.should_only_violations_by_forbidden_import
        )

    def _create_other_violating_dependencies_message(
        self,
        violating_dependencies: List[StrictDependency],
    ) -> List[RuleViolatedMessage]:
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

        return messages

    def _create_should_only_import_no_import_violated_messages(
        self, rule_violations: RuleViolations
    ) -> List[RuleViolatedMessage]:
        return self._create_no_import_between_original_subject_and_objects_message(
            rule_violations.should_only_violations_by_no_import
        )

    def _create_should_not_import_violated_messages(
        self, rule_violations: RuleViolations
    ) -> List[RuleViolatedMessage]:
        return self._create_other_violating_dependencies_message(
            rule_violations.should_not_violations
        )

    def _create_should_import_except_violated_messages(
        self, rule_violations: RuleViolations
    ) -> List[RuleViolatedMessage]:
        return self._create_no_import_other_than_between_original_subject_and_objects_message(
            rule_violations.should_except_violations
        )

    def _create_no_import_other_than_between_original_subject_and_objects_message(
        self, rule_violations: List[StrictDependency]
    ) -> List[RuleViolatedMessage]:
        messages = []

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

            if rule_objects:
                combined_rule_object = ANY_MODULE_THAT_IS_NOT + ", ".join(rule_objects)
                rule_subject_formatted = self._get_rule_subject_formatted(rule_subject)
                messages.append(
                    RuleViolatedMessage(
                        rule_subject_formatted, rule_verb, combined_rule_object
                    )
                )

        return messages

    def _create_should_only_import_except_violated_messages(
        self, rule_violations: RuleViolations
    ) -> List[RuleViolatedMessage]:
        messages = []

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
    ) -> List[RuleViolatedMessage]:
        return self._create_other_violating_dependencies_message(
            rule_violations.should_only_except_violations_by_forbidden_import
        )

    def _create_should_only_import_except_no_import_violated_messages(
        self, rule_violations: RuleViolations
    ) -> List[RuleViolatedMessage]:
        return self._create_no_import_other_than_between_original_subject_and_objects_message(
            rule_violations.should_only_except_violations_by_no_import
        )

    def _create_should_not_import_except_violated_messages(
        self, rule_violations: RuleViolations
    ) -> List[RuleViolatedMessage]:
        return self._create_other_violating_dependencies_message(
            rule_violations.should_not_except_violations
        )

    def _generate_rule_xbject_names_and_count(
        self, original_rule_xbjects: List[Module]
    ) -> Tuple[List[str], Dict[str, bool]]:
        names = []
        is_singular = {}

        for rule_object in original_rule_xbjects:
            module_name = self._get_module_name(rule_object)
            names.append(module_name)
            is_singular[module_name] = self._is_singular_module(rule_object)

        return names, is_singular

    def _get_module_name(self, module: Module) -> str:
        return module.name if module.name is not None else module.parent_module

    def _is_singular_module(self, module: Module) -> bool:
        return module.name is not None

    def _get_verb_prefix(self, negated: bool, subject_singular: bool) -> str:
        return PREFIX_MAPPING[(self._import_rule, negated, subject_singular)]

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
        self, dependency: StrictDependency
    ) -> Tuple[str, str]:
        rule_subject_name = self._get_module_name(dependency[0])
        rule_object_name = self._get_module_name(dependency[1])

        return self._get_quoted_name(rule_subject_name), self._get_quoted_name(
            rule_object_name
        )

    def _get_verb_suffix(self, subject_singular: bool) -> str:
        if not subject_singular:
            return ""

        if self._import_rule:
            return THIRD_PERSON_SINGULAR

        # "is imported by" does not need an additional 's'
        return ""
