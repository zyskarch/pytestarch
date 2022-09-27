# Welcome to PyTestArch

PyTestArch is an open source library that allows users to define architectural rules and test their code against them. It is 
generally inspired by [ArchUnit](https://www.archunit.org/).

## Installation Guide
PyTestArch is available via [PyPI](https://pypi.org/project/pytestarch/) and can be installed e.g. via pip: `pip install pytestarch`.

## Usage Guide
Three steps are required to test an architectural rule:

1) Create an evaluable representation of the source code you want to test

```
from pytestarch.pytestarch import get_evaluable_architecture

evaluable = get_evaluable_architecture("/home/dummy/project", "/home/dummy/project/src")
```
This will scan all python files under /home/dummy/project/src for imports and build an internal representation that can
later be queried. The first parameter /home/dummy/project helps PyTestArch to differentiate between internal and external 
dependencies. This evaluable can be used for multiple architectural rule checks; if you are using [pytest](https://docs.pytest.org/en/7.1.x/),
you could use a fixture for this evaluable object.

2) Define an architectural rule
```
from pytestarch.query_language.base_language import Rule

rule = Rule()
        .modules_that()
        .are_named("src.moduleB")
        .should_not()
        .be_imported_by_modules_that()
        .are_sub_modules_of("src.moduleA"),
```

This rule represents the architectural requirements that a module named "src.moduleB" should not be imported by any module
that is a submodule of "src.moduleA", excluding "src.moduleA" itself.

3) Evaluate your code against this rule

```
rule.assert_applies(evaluable)
```
That's it!
