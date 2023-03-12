from __future__ import annotations

from dataclasses import dataclass, fields
from typing import List

from pytestarch.eval_structure.evaluable_architecture import StrictDependency


@dataclass
class RuleViolations:
    should_violations: List[StrictDependency]
    should_only_violations_by_forbidden_import: List[StrictDependency]
    should_only_violations_by_no_import: List[StrictDependency]
    should_not_violations: List[StrictDependency]
    should_except_violations: List[StrictDependency]
    should_only_except_violations_by_forbidden_import: List[StrictDependency]
    should_only_except_violations_by_no_import: List[StrictDependency]
    should_not_except_violations: List[StrictDependency]

    def __bool__(self) -> bool:
        return any(self.__dict__[field.name] for field in fields(self))
