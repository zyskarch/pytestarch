from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Config:
    """Configuration of the file parser.

    Attributes:
        excluded_directories: Directory paths not to include in parsing specified via regex. Can be used to exclude
        e.g. test directories.
        excluded_external_dependencies: All external dependencies matching these patterns shall be excluded.
    """

    excluded_directories: tuple[str, ...]
