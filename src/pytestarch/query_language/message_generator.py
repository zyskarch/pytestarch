"""Converts a RuleViolations object into a human-readable format."""

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple

from pytestarch.eval_structure.evaluable_architecture import Module, StrictDependency
from pytestarch.query_language.rule_matcher import RuleViolations

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

    def __init__(
        self,
        original_rule_subject: Module,
        original_rule_objects: List[Module],
        import_rule: bool,
    ) -> None:
        """
        Args:
            original_rule_subject: module as originally specified
            original_rule_objects: modules as originally specified
            import_rule: True if the underlying rule is a "import" instead of an "is imported" rule
        """
        self._original_rule_subject_name = self._generate_rule_subject_name(
            original_rule_subject
        )
        self._original_rule_subject_singular = self._is_singular_module(
            original_rule_subject
        )

        (
            self._original_rule_object_names,
            self._original_rule_object_singular,
        ) = self._generate_rule_object_names_and_count(original_rule_objects)

        self._import_rule = import_rule

        self._base_verb = IMPORT if self._import_rule else IMPORTED_BY

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
        if not rule_violations.should_violated:
            return []

        return self._create_no_import_between_original_subject_and_objects_message()

    def _create_no_import_between_original_subject_and_objects_message(
        self,
    ) -> List[RuleViolatedMessage]:
        messages = []

        rule_subject = self._original_rule_subject_name

        verb_prefix = self._get_verb_prefix(
            negated=True, subject_singular=self._original_rule_subject_singular
        )
        rule_verb = self._concatenate_verb(prefix=verb_prefix, verb=self._base_verb)

        rule_objects = []

        for rule_object, is_singular in zip(
            self._original_rule_object_names, self._original_rule_object_singular
        ):
            rule_objects.append(self._get_rule_object(rule_object, is_singular))

        combined_rule_object = ", ".join(rule_objects)
        messages.append(
            RuleViolatedMessage(rule_subject, rule_verb, combined_rule_object)
        )

        return messages

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
        if not rule_violations.should_only_violated_by_forbidden_import:
            return []

        violating_dependencies = rule_violations.lax_dependencies.values()
        return self._create_other_violating_dependencies_message(violating_dependencies)

    def _create_other_violating_dependencies_message(
        self,
        violating_dependencies: Iterable[List[StrictDependency]],
    ) -> List[RuleViolatedMessage]:
        # messages are always of the type "module x imports module y"
        messages = []

        verb_prefix = self._get_verb_prefix(negated=False, subject_singular=True)
        suffix = self._get_verb_suffix(subject_singular=True)
        rule_verb = self._concatenate_verb(
            prefix=verb_prefix, verb=self._base_verb, suffix=suffix
        )

        for strict_dependencies in violating_dependencies:
            for strict_dependency in strict_dependencies:
                (
                    rule_subject,
                    rule_object,
                ) = self._get_rule_subject_and_object_of_strict_dependency(
                    strict_dependency
                )
                messages.append(
                    RuleViolatedMessage(rule_subject, rule_verb, rule_object)
                )

        return messages

    def _create_should_only_import_no_import_violated_messages(
        self, rule_violations: RuleViolations
    ) -> List[RuleViolatedMessage]:
        if not rule_violations.should_only_violated_by_no_import:
            return []

        return self._create_no_import_between_original_subject_and_objects_message()

    def _create_should_not_import_violated_messages(
        self, rule_violations: RuleViolations
    ) -> List[RuleViolatedMessage]:
        if not rule_violations.should_not_violated:
            return []

        violating_dependencies = rule_violations.strict_dependencies.values()
        return self._create_other_violating_dependencies_message(violating_dependencies)

    def _create_should_import_except_violated_messages(
        self, rule_violations: RuleViolations
    ) -> List[RuleViolatedMessage]:
        if not rule_violations.should_except_violated:
            return []

        return (
            self._create_no_import_other_than_between_original_subject_and_objects_message()
        )

    def _create_no_import_other_than_between_original_subject_and_objects_message(
        self,
    ) -> List[RuleViolatedMessage]:
        messages = []

        rule_subject = self._original_rule_subject_name

        verb_prefix = self._get_verb_prefix(
            negated=True, subject_singular=self._original_rule_subject_singular
        )
        rule_verb = self._concatenate_verb(prefix=verb_prefix, verb=self._base_verb)

        rule_objects = []

        for rule_object, is_singular in zip(
            self._original_rule_object_names, self._original_rule_object_singular
        ):
            rule_objects.append(
                self._get_rule_object(rule_object, is_singular),
            )

        combined_rule_object = ANY_MODULE_THAT_IS_NOT + ", ".join(rule_objects)
        messages.append(
            RuleViolatedMessage(rule_subject, rule_verb, combined_rule_object)
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
        if not rule_violations.should_only_except_violated_by_forbidden_import:
            return []

        violating_dependencies = rule_violations.strict_dependencies.values()
        return self._create_other_violating_dependencies_message(violating_dependencies)

    def _create_should_only_import_except_no_import_violated_messages(
        self, rule_violations: RuleViolations
    ) -> List[RuleViolatedMessage]:
        if not rule_violations.should_only_except_violated_by_no_import:
            return []

        return (
            self._create_no_import_other_than_between_original_subject_and_objects_message()
        )

    def _create_should_not_import_except_violated_messages(
        self, rule_violations: RuleViolations
    ) -> List[RuleViolatedMessage]:
        if not rule_violations.should_not_except_violated:
            return []

        violating_dependencies = rule_violations.lax_dependencies.values()
        return self._create_other_violating_dependencies_message(violating_dependencies)

    def _generate_rule_subject_name(self, module: Module) -> str:
        name = self._get_module_name(module)
        prefix = ""
        if not self._is_singular_module(module):
            prefix = "Sub modules of "
        return f"{prefix}{self._quoted_name(name)}"

    def _generate_rule_object_names_and_count(
        self, original_rule_objects: List[Module]
    ) -> Tuple[List[str], List[bool]]:
        names = []
        is_singular = []

        for rule_object in original_rule_objects:
            names.append(self._get_module_name(rule_object))
            is_singular.append(self._is_singular_module(rule_object))

        return names, is_singular

    def _get_module_name(self, module: Module) -> str:
        return module.name if module.name is not None else module.parent_module

    def _is_singular_module(self, module: Module) -> bool:
        return module.name is not None

    def _get_verb_prefix(self, negated: bool, subject_singular: bool) -> str:
        return PREFIX_MAPPING[(self._import_rule, negated, subject_singular)]

    def _concatenate_verb(self, verb: str, prefix: str = "", suffix="") -> str:
        return f"{prefix}{verb}{suffix}"

    def _get_rule_object(self, rule_object: str, is_singular: bool) -> str:
        module_qualifier = "" if is_singular else RULE_OBJECT_IS_SUBMODULE_MARKER
        return f"{module_qualifier}{self._quoted_name(rule_object)}"

    def _quoted_name(self, name: str) -> str:
        return f'"{name}"'

    def _get_rule_subject_and_object_of_strict_dependency(
        self, strict_dependency: StrictDependency
    ) -> Tuple[str, str]:
        # strict dependency is always reported in format (importer, importee)
        # if rule is of format A ... imports B, the dependency will be (A, B)
        if self._import_rule:
            rule_subject, rule_object = strict_dependency
        else:
            rule_object, rule_subject = strict_dependency

        rule_subject_name = self._get_module_name(rule_subject)
        rule_object_name = self._get_module_name(rule_object)

        return self._quoted_name(rule_subject_name), self._quoted_name(rule_object_name)

    def _get_verb_suffix(self, subject_singular: bool) -> str:
        if not subject_singular:
            return ""

        if self._import_rule:
            return THIRD_PERSON_SINGULAR

        # "is imported by" does not need an additional 's'
        return ""
