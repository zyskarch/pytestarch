from __future__ import annotations

from src.moduleB.fileB import b  # type: ignore


def test_c():
    b()
