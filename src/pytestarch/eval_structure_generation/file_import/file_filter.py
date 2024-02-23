from __future__ import annotations

import re
from pathlib import Path

from pytestarch.eval_structure_generation.file_import.config import Config

ALL_MARKER = "*"


class FileFilter:
    """Uses a pseudo-regex pattern to determine whether a file or directory should be excluded.

    Allowed patterns are:
    - *A*: file or dir will be excluded, if 'A' is part of their name
    - *A: file or dir will be excluded, if their name ends with 'A'
    - A*: file or dir will be excluded, if their name starts with 'A'
    - A: file or dir will be excluded, if their name is 'A'
    """

    def __init__(self, config: Config) -> None:
        self._excluded_directories = [
            re.compile(directory_pattern)
            for directory_pattern in config.excluded_directories
        ]

    def is_excluded(self, path: Path) -> bool:
        """Returns True if the path matches one of the pre-configured exclusion patterns."""
        path_as_str = str(path)

        return any(
            re.match(pattern, path_as_str) is not None
            for pattern in self._excluded_directories
        )
