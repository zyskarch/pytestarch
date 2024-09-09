from __future__ import annotations

import re
from functools import singledispatchmethod
from pathlib import Path

from pytestarch.eval_structure_generation.file_import.config import Config

ALL_MARKER = "*"


class FileFilter:
    """Uses a regex pattern to determine whether a file or directory should be excluded."""

    def __init__(self, config: Config) -> None:
        self._excluded_directories = [
            re.compile(directory_pattern)
            for directory_pattern in config.excluded_directories
        ]

    @singledispatchmethod
    def is_excluded(self, obj: str | Path) -> bool:
        """Returns True if the object matches one of the pre-configured exclusion patterns."""
        raise NotImplementedError

    @is_excluded.register(Path)
    def _(self, obj: Path) -> bool:
        path_as_str = str(obj)

        return self.is_excluded(path_as_str)

    @is_excluded.register(str)
    def _(self, obj: str) -> bool:
        return any(
            re.match(pattern, obj) is not None for pattern in self._excluded_directories
        )

    def has_filter(self) -> bool:
        return len(self._excluded_directories) > 0
