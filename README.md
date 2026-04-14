# Welcome to PyTestArch

PyTestArch is an open source library that allows users to define architectural rules and test their code against them. It is 
generally inspired by [ArchUnit](https://www.archunit.org/).

## Installation Guide
PyTestArch is available via [PyPI](https://pypi.org/project/pytestarch/) and can be installed e.g. via pip: `pip install pytestarch`. To also install the
optional dependency matplotlib, which is required to draw the created dependency graphs, install `pytestarch[visualization]`

## Usage Guide
Three steps are required to test an architectural rule:

1) Create an evaluable representation of the source code you want to test

```
from pytestarch import get_evaluable_architecture

evaluable = get_evaluable_architecture("/home/dummy/project", "/home/dummy/project/src")
```
This will scan all python files under /home/dummy/project/src for imports and build an internal representation that can
later be queried. The first parameter /home/dummy/project helps PyTestArch to differentiate between internal and external 
dependencies. This evaluable can be used for multiple architectural rule checks; if you are using [pytest](https://docs.pytest.org/en/7.1.x/),
you could use a fixture for this evaluable object.

2) Define an architectural rule
```
from pytestarch import Rule

rule = (
    Rule() 
    .modules_that() 
    .are_named("project.src.moduleB") 
    .should_not() 
    .be_imported_by_modules_that() 
    .are_sub_modules_of("project.src.moduleA") 
)
```

This rule represents the architectural requirements that a module named "project.src.moduleB" should not be imported by any module
that is a submodule of "project.src.moduleA", excluding "project.src.moduleA" itself.

3) Evaluate your code against this rule

```
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
