"""Experimental predefined architecture rules.

The rules provided in this subpackage are drafts of predefined architecture
checks (e.g. Onion Architecture or a generic layered architecture, inspired by
ArchUnit's predefined rules) on top of the regular layer rule syntax. Their API
is not finalized yet and may change or be removed without notice. Feedback on
the currently offered rules is very welcome (see
https://github.com/zyskarch/pytestarch/issues/134).
"""

from pytestarch.experimental.layered_architecture import (
    PredefinedLayeredArchitecture,
    layered_architecture,
)
from pytestarch.experimental.onion_architecture import (
    OnionArchitecture,
    onion_architecture,
)

__all__ = [
    "PredefinedLayeredArchitecture",
    "layered_architecture",
    "OnionArchitecture",
    "onion_architecture",
]
