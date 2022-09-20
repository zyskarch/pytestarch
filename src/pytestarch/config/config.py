from dataclasses import dataclass
from typing import Tuple


@dataclass
class Config:
    """Configuration of the file parser.

    Attributes:
        excluded_directories: Directory paths not to include in parsing. Can be used to exclude e.g. test directories.
    """

    excluded_directories: Tuple[str, ...]
