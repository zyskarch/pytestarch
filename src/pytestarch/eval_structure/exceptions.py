from __future__ import annotations


class ImpossibleMatch(Exception):
    pass


class LayerMismatch(Exception):
    pass


class ModuleUnknown(Exception):
    """Raised when a queried module is not present in the dependency graph.

    The exception message includes actionable guidance on common causes,
    such as the module being an external library that was excluded from the
    graph or the module name being misspelled.
    """
