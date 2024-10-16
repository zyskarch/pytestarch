from __future__ import annotations

import io as io_import  # noqa: F401
import sys  # noqa: F401
import typing
from ast import *  # noqa: F403
from os import path as p  # noqa: F401
from os import read  # noqa: F401
from pathlib import Path

import pytest  # noqa: F401

from pytestarch.pytestarch import get_evaluable_architecture

from . import test_dummy_2, test_dummy_3  # noqa: F401


class A:
    pass


ROOT_PATH = Path(__file__).parent.parent.parent.parent.parent.resolve()
ROOT_PATH_STR: typing.Final[str] = str(ROOT_PATH)
MODULE_PATH_STR: typing.Final[str] = str(ROOT_PATH / "tests/resources")


def dummy_test() -> None:
    get_evaluable_architecture(ROOT_PATH_STR, MODULE_PATH_STR)
    import itertools  # noqa: F401

    assert True
