# Welcome to PyTestArch

PyTestArch is an open source library that allows users to define architectural rules and test their code against them. It is 
generally inspired by [ArchUnit](https://www.archunit.org/).

## Installation Guide
PyTestArch is available via [PyPI](https://pypi.org/project/pytestarch/) and can be installed e.g. via pip: `pip install pytestarch`. To also install the
optional dependency matplotlib, which is required to draw the created dependency graphs, install `pytestarch[visualization]`.

## Usage Guide
Three steps are required to test an architectural rule:

1. Create an evaluable representation of the source code you want to test

    ```python
    from pytestarch import get_evaluable_architecture

    evaluable = get_evaluable_architecture("/home/dummy/project/src", mode="multi_module")
    ```
    This treats `/home/dummy/project/src` as the import root, scans every Python file below it, and builds the
    dependency graph used by rules. `module_path` defaults to the root; pass it to scan only a subdirectory. Module
    names are import names (`moduleB` for packages directly under `src`, or `src.moduleB` if `src` is itself a
    package, or if the repository root is passed instead). `mode="legacy"` keeps the historical directory-prefixed
    names and disables cross-package resolution.
    See the [scan modes guide](features/general.md#scan-modes). Reuse the evaluable across rules, for example in a
    [pytest](https://docs.pytest.org/) fixture.

2. Define an architectural rule

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

3. Evaluate your code against this rule

    ```python
    rule.assert_applies(evaluable)
    ```
    That's it!
