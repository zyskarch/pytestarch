from __future__ import annotations

from dataclasses import dataclass, fields
from typing import List, Optional

from pytestarch.eval_structure.evaluable_architecture import (
    DependenciesByBaseModules,
    UnexpectedDependenciesByBaseModule,
)


@dataclass
class RuleViolations:
    unexpected_dependencies: Optional[UnexpectedDependenciesByBaseModule]
    dependencies: Optional[DependenciesByBaseModules]

    should_violated: bool = False
    should_only_violated_by_forbidden_import: bool = False
    should_only_violated_by_no_import: bool = False
    should_not_violated: bool = False
    should_except_violated: bool = False
    should_only_except_violated_by_forbidden_import: bool = False
    should_only_except_violated_by_no_import: bool = False
    should_not_except_violated: bool = False

    def __bool__(self) -> bool:
        return any(self.__dict__[a] for a in self._bool_field_names())

    @classmethod
    def _bool_field_names(cls) -> List[str]:
        return [field.name for field in fields(cls) if field.type == "bool"]
