from __future__ import annotations

from dataclasses import dataclass, fields

from pytestarch.eval_structure.evaluable_architecture import Dependency


@dataclass
class RuleViolations:
    should_violations: set[Dependency]
    should_only_violations_by_forbidden_import: set[Dependency]
    should_only_violations_by_no_import: set[Dependency]
    should_not_violations: set[Dependency]
    should_except_violations: set[Dependency]
    should_only_except_violations_by_forbidden_import: set[Dependency]
    should_only_except_violations_by_no_import: set[Dependency]
    should_not_except_violations: set[Dependency]

    def __bool__(self) -> bool:
        return any(self.__dict__[field.name] for field in fields(self))
