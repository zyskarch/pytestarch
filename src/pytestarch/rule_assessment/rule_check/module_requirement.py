from __future__ import annotations

from collections.abc import Sequence

from pytestarch.eval_structure.evaluable_architecture import ModuleFilter


class ModuleRequirement:
    """Stores information about which module is supposed to be checked against which module."""

    def __init__(
        self,
        importers: Sequence[ModuleFilter],
        importees: Sequence[ModuleFilter],
        importer_specified_as_rule_subject: bool,
    ) -> None:
        self._importer_as_specified_by_user = importers
        self._importees_as_specified_by_user = importees

        self._importers = importers
        self._importees = importees

        self._importer_specified_as_rule_subject = importer_specified_as_rule_subject

        if self.rule_specified_with_importer_as_rule_object:
            self._importers, self._importees = (
                self._importees,
                self._importers,
            )

    @property
    def importers(self) -> Sequence[ModuleFilter]:
        return self._importers

    @property
    def importees(self) -> Sequence[ModuleFilter]:
        return self._importees

    @property
    def importers_as_specified_by_user(self) -> Sequence[ModuleFilter]:
        return self._importer_as_specified_by_user

    @property
    def importees_as_specified_by_user(self) -> Sequence[ModuleFilter]:
        return self._importees_as_specified_by_user

    @property
    def rule_specified_with_importer_as_rule_object(self) -> bool:
        # True if rule is of format "is imported by"
        return not self._importer_specified_as_rule_subject

    @property
    def rule_specified_with_importer_as_rule_subject(self) -> bool:
        # True if rule is of format "imports"
        return self._importer_specified_as_rule_subject
