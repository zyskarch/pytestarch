# Welcome to PyTestArch

PyTestArch is an open source library that allows users to define architectural rules and test their code against them. It is 
generally inspired by [ArchUnit](https://www.archunit.org/).

## Installation Guide
PyTestArch is available via [PyPI](https://pypi.org/project/pytestarch/) and can be installed e.g. via pip: `pip install pytestarch`. To also install the
optional dependency matplotlib, which is required to draw the created dependency graphs, install `pytestarch[visualization]`

## Usage Guide
Three steps are required to test an architectural rule:

1) Create an evaluable representation of the source code you want to test

```python
from pytestarch import get_evaluable_architecture

evaluable = get_evaluable_architecture("/home/dummy/project/src", mode="multi_module")
```
This treats `/home/dummy/project/src` as the import root, scans every Python file below it, and builds the
dependency graph used by rules. `module_path` defaults to the root; pass it to scan only a subdirectory. Module
names are import names (`moduleB` for packages directly under `src`, or `src.moduleB` if `src` is itself a
package, or if the repository root is passed instead). `mode="legacy"` keeps the historical directory-prefixed
names and disables cross-package resolution.
See the [scan modes guide](https://zyskarch.github.io/pytestarch/latest/features/general/#scan-modes).
Reuse the evaluable across rules, for example in a [pytest](https://docs.pytest.org/) fixture.

2) Define an architectural rule
```python
from pytestarch import Rule

rule = (
    Rule()
    .modules_that()
    .are_named("moduleB")
    .should_not()
    .be_imported_by_modules_that()
    .are_sub_modules_of("moduleA")
)
```

This rule represents the architectural requirements that a module named "moduleB" should not be imported by any module
that is a submodule of "moduleA", excluding "moduleA" itself.

3) Evaluate your code against this rule

```python
rule.assert_applies(evaluable)
```
That's it!

## Real-World Example

The snippet below is taken directly from pytestarch's own architecture tests
([`tests/test_architecture.py`](https://github.com/zyskarch/pytestarch/blob/main/tests/test_architecture.py)).
It guards the library's own internal module boundaries

```python
from __future__ import annotations

from pathlib import Path

import pytest

from pytestarch import EvaluableArchitecture, Rule, get_evaluable_architecture


@pytest.fixture(scope="session")
def pytestarch_architecture() -> EvaluableArchitecture:
    cwd = Path.cwd()
    while cwd.stem != "pytestarch":
        cwd = cwd.parent
    src_folder = str(cwd / "src/pytestarch")

    return get_evaluable_architecture(
        src_folder,
        src_folder,
        ("*__pycache__", "*__init__.py"),
    )


BASE_MODULE = "pytestarch"
DIAGRAM = f"{BASE_MODULE}.diagram_extension"
STRUCTURE = f"{BASE_MODULE}.eval_structure"
GENERATION = f"{BASE_MODULE}.eval_structure_generation"
LANGUAGE = f"{BASE_MODULE}.query_language"
ASSESSMENT = f"{BASE_MODULE}.rule_assessment"
UTILS = f"{BASE_MODULE}.utils"


top_level_rules = [
    pytest.param(
        Rule()
        .modules_that()
        .are_named(DIAGRAM)
        .should_only()
        .import_modules_that()
        .are_named([LANGUAGE, STRUCTURE]),
        id="diagram_extension",
    ),
    pytest.param(
        Rule().modules_that().are_named(STRUCTURE).should_not().import_anything(),
        id="eval_structure",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(GENERATION)
        .should_only()
        .import_modules_that()
        .are_named(STRUCTURE),
        id="eval_structure_generation",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(LANGUAGE)
        .should_only()
        .import_modules_that()
        .are_named([STRUCTURE, ASSESSMENT, UTILS]),
        id="query_language",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(ASSESSMENT)
        .should_only()
        .import_modules_that()
        .are_named(STRUCTURE),
        id="rule_assessment",
    ),
]


@pytest.mark.parametrize("rule", top_level_rules)
def test_top_level_module_structure(
    rule: Rule, pytestarch_architecture: EvaluableArchitecture
) -> None:
    rule.assert_applies(pytestarch_architecture)
```

## Further Resources

- [Full documentation](https://zyskarch.github.io/pytestarch/latest)
- More test examples on GitHub:
  - [`tests/test_architecture.py`](https://github.com/zyskarch/pytestarch/blob/main/tests/test_architecture.py) — module boundary rules (shown above)
  - [`tests/diagram_extension/`](https://github.com/zyskarch/pytestarch/tree/main/tests/diagram_extension) — generating rules from PlantUML diagrams
  - [`tests/integration/`](https://github.com/zyskarch/pytestarch/tree/main/tests/integration) — extensive parametrized test cases
