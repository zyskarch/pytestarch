from pathlib import Path

from pytestarch.eval_structure_generation.file_import.config import Config
from pytestarch.eval_structure_generation.file_import.file_filter import FileFilter


class MockFileFilter(FileFilter):
    def __init__(self):
        super().__init__(Config(tuple()))

    def is_excluded(self, path: Path) -> bool:
        return False
