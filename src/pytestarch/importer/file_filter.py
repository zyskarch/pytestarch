from pathlib import Path

from pytestarch.config.config import Config

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
        self._excluded_dirs = set()
        self._excluded_prefixes = set()
        self._excluded_suffixes = set()
        self._excluded_infixes = set()

        for dir in config.excluded_directories:
            if dir.startswith(ALL_MARKER) and dir.endswith(ALL_MARKER):
                self._excluded_infixes.add(dir[1:-1])
            elif dir.startswith(ALL_MARKER):
                self._excluded_suffixes.add(dir[1:])
            elif dir.endswith(ALL_MARKER):
                self._excluded_prefixes.add(dir[:-1])
            else:
                self._excluded_dirs.add(dir)

    def is_excluded(self, path: Path) -> bool:
        """Returns True if the path matches one of the pre-configured exclusion patterns."""
        path = str(path)

        full_excluded = path in self._excluded_dirs
        prefix_excluded = any(
            [True for prefix in self._excluded_prefixes if path.startswith(prefix)]
        )
        suffix_excluded = any(
            [True for suffix in self._excluded_suffixes if path.endswith(suffix)]
        )
        infix_excluded = any(
            [True for infix in self._excluded_infixes if infix in path]
        )

        return full_excluded or prefix_excluded or suffix_excluded or infix_excluded
