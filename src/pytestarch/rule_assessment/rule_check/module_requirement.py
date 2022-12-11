from typing import List, Union

from pytestarch.eval_structure.evaluable_architecture import Module


class ModuleRequirement:
    """Stores information about which module is supposed to be checked against which module."""

    def __init__(
        self,
        left_hand_module: Module,
        right_hand_modules: List[Module],
        import_relation: bool,
    ) -> None:
        self._left_hand_modules_as_specified_by_user = left_hand_module
        self._right_hand_modules_as_specified_by_user = right_hand_modules

        self._left_hand_modules = left_hand_module
        self._right_hand_modules = right_hand_modules

        self._right_hand_module_has_specifier = import_relation

        if self.left_hand_module_has_specifier:
            self._left_hand_modules, self._right_hand_modules = (
                self._right_hand_modules,
                self._left_hand_modules,
            )

    @property
    def left_hand_modules(self) -> Union[Module, List[Module]]:
        return self._left_hand_modules

    @property
    def right_hand_modules(self) -> Union[Module, List[Module]]:
        return self._right_hand_modules

    @property
    def left_hand_module_has_specifier(self) -> bool:
        # True if rule is of format "is imported by"
        return not self._right_hand_module_has_specifier
