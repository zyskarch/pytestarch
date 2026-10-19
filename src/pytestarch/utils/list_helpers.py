from __future__ import annotations

from collections.abc import Sequence


def listify(modules: str | Sequence[str], *, dedup: bool = False) -> list[str]:
    """Converts a module or sequence of modules into a list of modules.

    Args:
        modules: module or sequence of modules.
        dedup: if True, duplicate modules are removed while preserving the
            order of their first occurrence.

    Returns:
        the modules as a list.
    """
    result = [modules] if isinstance(modules, str) else list(modules)

    if dedup:
        return list(dict.fromkeys(result))

    return result
