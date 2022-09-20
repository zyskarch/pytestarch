from pathlib import Path

from pytestarch.config.config import Config
from pytestarch.importer.file_filter import FileFilter


class MockFileFilter(FileFilter):
    def __init__(self):
        super().__init__(Config(tuple()))

    def is_excluded(self, path: Path) -> bool:
        return False
