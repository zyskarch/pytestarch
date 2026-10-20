from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

import pytest

from pytestarch.eval_structure_generation.file_import.config import Config
from pytestarch.eval_structure_generation.file_import.file_filter import FileFilter
from pytestarch.eval_structure_generation.file_import.parser import Parser
from pytestarch.utils.partial_match_to_regex_converter import (
    convert_partial_match_to_regex,
)

SOURCE_ROOT = Path(__file__).parent.parent
RESOURCES_DIR = SOURCE_ROOT / "resources/importer"


def _symlink_or_skip(target: Path, link: Path, is_directory: bool = False) -> None:
    try:
        link.symlink_to(target, target_is_directory=is_directory)
    except (NotImplementedError, OSError):
        pytest.skip("symlinks are not supported on this platform")


def _package_and_external_module(tmp_path: Path) -> tuple[Path, Path]:
    source = tmp_path / "package"
    source.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "module.py").write_text("x = 1")
    return source, outside


def test_parser_parses_all_files_in_directory() -> None:
    parser = Parser(
        FileFilter(Config((convert_partial_match_to_regex("*__pycache__"),))),
        SOURCE_ROOT,
    )

    all_modules, parsed_modules = parser.parse(RESOURCES_DIR)

    assert len(all_modules) == 22
    assert len(parsed_modules) == 14

    expected_modules = {
        "tests.resources.importer.file",
        "tests.resources.importer.level0.level1.level2.__init__",
        "tests.resources.importer.level0.test_dummy_3",
        "tests.resources.importer.level0.level1.level2.level3.level4.level5.module_level_5",
        "tests.resources.importer.level0.test_dummy_2",
        "tests.resources.importer.sub_dir.__init__",
        "tests.resources.importer.level0.DummyTest",
        "tests.resources.importer.level0.level1.level2.level3.level4.level5.__init__",
        "tests.resources.importer.level0.level1.level2.level3.__init__",
        "tests.resources.importer.__init__",
        "tests.resources.importer.level0.level1.__init__",
        "tests.resources.importer.level0.test_dummy",
        "tests.resources.importer.level0.level1.level2.level3.level4.__init__",
        "tests.resources.importer.level0.__init__",
    }

    assert set(map(lambda module: module.name, parsed_modules)) == expected_modules


def test_parser_prefixes_module_names_with_root_dir_name(tmp_path) -> None:
    """Module names are prefixed with the root directory's name - no matter whether
    the root directory contains an __init__.py."""
    (tmp_path / "pkg_a").mkdir()
    (tmp_path / "pkg_a" / "__init__.py").write_text("")
    (tmp_path / "pkg_a" / "mod.py").write_text("x = 1")

    parser = Parser(FileFilter(Config(())), tmp_path)

    all_modules, parsed_modules = parser.parse(tmp_path)

    prefix = f"{tmp_path.name}."
    assert set(map(lambda module: module.name, parsed_modules)) == {
        f"{prefix}pkg_a.__init__",
        f"{prefix}pkg_a.mod",
    }
    assert set(all_modules) == {
        tmp_path.name,
        f"{prefix}pkg_a",
        f"{prefix}pkg_a.__init__",
        f"{prefix}pkg_a.mod",
    }


@pytest.mark.parametrize(
    "contents",
    [
        "print('content')",
        "print('「content」😭')",
    ],
)
def test_parser_reads_special_chars(tmp_path, contents) -> None:
    """
    Tests that parser handles special chars in the file it parses.
    """
    code_file = tmp_path / "code.py"
    code_file.write_text(contents, encoding="utf-8")
    result: subprocess.CompletedProcess = subprocess.run(  # noqa:S603 // Input is entirely controlled by test.
        [
            sys.executable,
            "-c",
            f"""
from pytestarch.eval_structure_generation import file_import as fi
from pytestarch.utils.partial_match_to_regex_converter import (
    convert_partial_match_to_regex,
)
from pathlib import Path
fi.parser.Parser(
    fi.file_filter.FileFilter(fi.config.Config((convert_partial_match_to_regex("*__pycache__"),))),
    Path("{tmp_path!s}")
).parse(Path("{tmp_path!s}"))
            """,
        ],
        env={
            **os.environ,
            **{
                "LC_ALL": "C",
                "PYTHONUTF8": "0",
                "LANG": "C",
                "PYTHONCOERCELOCALE": "0",
            },
        },
        capture_output=True,
    )

    assert "UnicodeDecodeError" not in result.stderr.decode("utf-8"), (
        "Parser fails to parse code files with utf-8 character contents."
    )


def test_parser_parses_single_file_as_walk_start(tmp_path: Path) -> None:
    """A single .py file as the walk start yields exactly that file's module,
    named as in the directory walk."""
    source = tmp_path / "package"
    source.mkdir()
    (source / "module.py").write_text("x = 1")

    parser = Parser(FileFilter(Config(())), source)
    all_modules, parsed_modules = parser.parse(source / "module.py")

    assert all_modules == ["package.module"]
    assert [module.name for module in parsed_modules] == ["package.module"]


def test_parser_keeps_names_for_each_symlinked_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "package"
    real = source / "real"
    real.mkdir(parents=True)
    (real / "module.py").write_text("x = 1")
    _symlink_or_skip(real, source / "alias", is_directory=True)

    parse_calls: list[bytes] = []
    original_parse = ast.parse

    def counting_parse(source_code: bytes) -> ast.Module:
        parse_calls.append(source_code)
        return original_parse(source_code)

    monkeypatch.setattr(ast, "parse", counting_parse)

    parser = Parser(FileFilter(Config(())), source)
    all_modules, parsed_modules = parser.parse(source)

    assert set(all_modules) == {
        "package",
        "package.alias",
        "package.alias.module",
        "package.real",
        "package.real.module",
    }
    assert set(map(lambda module: module.name, parsed_modules)) == {
        "package.alias.module",
        "package.real.module",
    }
    assert len(parse_calls) == 1


def test_parser_accepts_symlinked_directory_outside_root_as_walk_start(
    tmp_path: Path,
) -> None:
    """The link keeps its link name, and a cycle through it terminates."""
    source, outside = _package_and_external_module(tmp_path)
    _symlink_or_skip(outside, outside / "self", is_directory=True)
    linked = source / "linked"
    _symlink_or_skip(outside, linked, is_directory=True)

    code = """
import sys
from pathlib import Path
from pytestarch.eval_structure_generation import file_import as fi
source, linked = sys.argv[1], sys.argv[2]
all_modules, _ = fi.parser.Parser(
    fi.file_filter.FileFilter(fi.config.Config(())),
    Path(source),
).parse(Path(linked))
print("\\n".join(sorted(all_modules)))
"""
    try:
        result = subprocess.run(  # noqa: S603 // input is controlled by the test.
            [sys.executable, "-c", code, str(source), str(linked)],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except subprocess.TimeoutExpired:
        pytest.fail("parser did not terminate on a symlink cycle")

    assert result.returncode == 0, result.stderr
    assert set(result.stdout.splitlines()) == {
        "package.linked",
        "package.linked.module",
    }


@pytest.mark.parametrize(
    "link_names, exclusions, expected_links",
    [
        pytest.param(
            ("aaa_alias", "zzz_alias"),
            (),
            ("aaa_alias", "zzz_alias"),
            id="all aliases",
        ),
        pytest.param(
            ("aaa_skip", "zzz_good"),
            ("*aaa_skip*",),
            ("zzz_good",),
            id="excluded alias",
        ),
    ],
)
def test_parser_walks_each_alias_for_outside_target(
    tmp_path: Path,
    link_names: tuple[str, str],
    exclusions: tuple[str, ...],
    expected_links: tuple[str, ...],
) -> None:
    source, outside = _package_and_external_module(tmp_path)
    for link_name in link_names:
        _symlink_or_skip(outside, source / link_name, is_directory=True)

    regex_exclusions = tuple(map(convert_partial_match_to_regex, exclusions))
    parser = Parser(FileFilter(Config(regex_exclusions)), source)
    all_modules, parsed_modules = parser.parse(source)

    expected_modules = {"package"}
    for link_name in expected_links:
        expected_modules.add(f"package.{link_name}")
        expected_modules.add(f"package.{link_name}.module")

    assert set(all_modules) == expected_modules
    assert set(map(lambda module: module.name, parsed_modules)) == {
        f"package.{link_name}.module" for link_name in expected_links
    }


def test_parser_names_and_filters_symlinked_file_by_link_path(tmp_path: Path) -> None:
    """File links keep the link path for naming and filtering."""
    source, outside = _package_and_external_module(tmp_path)
    _symlink_or_skip(outside / "module.py", source / "module.py")

    exclusions = (convert_partial_match_to_regex("*outside*"),)
    parser = Parser(FileFilter(Config(exclusions)), source)
    all_modules, parsed_modules = parser.parse(source)

    assert set(all_modules) == {"package", "package.module"}
    assert set(map(lambda module: module.name, parsed_modules)) == {"package.module"}


def test_parser_requires_py_suffix_on_link_path(tmp_path: Path) -> None:
    """The .py suffix is tested against the link path: a file link whose name
    lacks the suffix is not parsed as a module, since Python's finder matches
    the literal link name and could never import one."""
    source = tmp_path / "package"
    pkg = source / "pkg"
    pkg.mkdir(parents=True)
    (pkg / "real.py").write_text("x = 1")
    _symlink_or_skip(pkg / "real.py", pkg / "module")

    parser = Parser(FileFilter(Config(())), source)
    all_modules, parsed_modules = parser.parse(source)

    assert set(all_modules) == {"package", "package.pkg", "package.pkg.real"}
    assert set(map(lambda module: module.name, parsed_modules)) == {"package.pkg.real"}


def test_parser_surfaces_syntax_error_for_py_named_link_to_non_python_file(
    tmp_path: Path,
) -> None:
    """A .py-named link to a non-Python file passes the suffix test on the link
    path and is parsed from the resolved target's content, so the syntax error
    surfaces instead of the file being silently skipped."""
    source = tmp_path / "package"
    pkg = source / "pkg"
    pkg.mkdir(parents=True)
    (pkg / "data.txt").write_text("this is not python {")
    _symlink_or_skip(pkg / "data.txt", pkg / "x.py")

    parser = Parser(FileFilter(Config(())), source)
    with pytest.raises(SyntaxError):
        parser.parse(source)


def test_parser_applies_exclusions_to_walk_path(tmp_path: Path) -> None:
    """Excluding a directory does not exclude links to it under other names."""
    source = tmp_path / "package"
    hidden = source / "hidden"
    hidden.mkdir(parents=True)
    (hidden / "module.py").write_text("x = 1")
    _symlink_or_skip(hidden, source / "alias", is_directory=True)

    exclusions = (convert_partial_match_to_regex("*hidden*"),)
    parser = Parser(FileFilter(Config(exclusions)), source)
    all_modules, parsed_modules = parser.parse(source)

    assert set(all_modules) == {
        "package",
        "package.alias",
        "package.alias.module",
    }
    assert set(map(lambda module: module.name, parsed_modules)) == {
        "package.alias.module"
    }


def test_parser_skips_broken_symlinks(tmp_path: Path) -> None:
    source = tmp_path / "package"
    source.mkdir()
    _symlink_or_skip(source / "missing.py", source / "broken.py")

    parser = Parser(FileFilter(Config(())), source)
    all_modules, parsed_modules = parser.parse(source)

    assert set(all_modules) == {"package"}
    assert parsed_modules == []


def test_parser_keeps_relative_source_root_relative(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A relative source root keeps the walk paths relative, so module names
    keep the relative path form the caller passed."""
    monkeypatch.chdir(tmp_path)
    source = tmp_path / "package"
    source.mkdir()
    (source / "module.py").write_text("x = 1")

    parser = Parser(FileFilter(Config(())), Path("package"))
    all_modules, parsed_modules = parser.parse(Path("package"))

    assert set(all_modules) == {"package", "package.module"}
    assert set(map(lambda module: module.name, parsed_modules)) == {"package.module"}
