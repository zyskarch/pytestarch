from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Set

from pytestarch.eval_structure.evaluable_architecture import StrictDependency


@dataclass
class RuleViolations:
    should_violations: Set[StrictDependency]
    should_only_violations_by_forbidden_import: Set[StrictDependency]
    should_only_violations_by_no_import: Set[StrictDependency]
    should_not_violations: Set[StrictDependency]
    should_except_violations: Set[StrictDependency]
    should_only_except_violations_by_forbidden_import: Set[StrictDependency]
    should_only_except_violations_by_no_import: Set[StrictDependency]
    should_not_except_violations: Set[StrictDependency]

    def __bool__(self) -> bool:
        return any(self.__dict__[field.name] for field in fields(self))
