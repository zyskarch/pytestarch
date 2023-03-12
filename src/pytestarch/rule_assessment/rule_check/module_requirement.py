from __future__ import annotations

from typing import List

from pytestarch.eval_structure.evaluable_architecture import Module


class ModuleRequirement:
    """Stores information about which module is supposed to be checked against which module."""

    def __init__(
        self,
        importers: List[Module],
        importees: List[Module],
        flip_importer_and_importees: bool,
    ) -> None:
        self._importer_as_specified_by_user = importers
        self._importees_as_specified_by_user = importees

        self._importers = importers
        self._importees = importees

        self._flip_importer_and_importees = flip_importer_and_importees

        if self.rule_specified_with_importer_as_rule_object:
            self._importers, self._importees = (
                self._importees,
                self._importers,
            )

    @property
    def importers(self) -> List[Module]:
        return self._importers

    @property
    def importees(self) -> List[Module]:
        return self._importees

    @property
    def importers_as_specified_by_user(self) -> list[Module]:
        return self._importer_as_specified_by_user

    @property
    def importees_as_specified_by_user(self) -> List[Module]:
        return self._importees_as_specified_by_user

    @property
    def rule_specified_with_importer_as_rule_object(self) -> bool:
        # True if rule is of format "is imported by"
        return not self._flip_importer_and_importees

    @property
    def rule_specified_with_importer_as_rule_subject(self) -> bool:
        # True if rule is of format "is imported by"
        return self._flip_importer_and_importees
