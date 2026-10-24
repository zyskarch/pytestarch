# Changelog

This project uses semantic versioning and follows [keep a changelog](https://keepachangelog.com).

## [5.1.0] -- 2026-10-24
### Added
- Experimental predefined architecture rules inspired by ArchUnit ([#134](https://github.com/zyskarch/pytestarch/issues/134)): `pytestarch.experimental.layered_architecture()` enforces a per-layer dependency whitelist, `pytestarch.experimental.onion_architecture()` implements the Onion Architecture style.

### Changed
- Dependency and packaging management moved from Poetry to [uv](https://docs.astral.sh/uv/): `pyproject.toml` now uses a `hatchling` build backend and PEP 735 dependency groups.
- Replaced mypy with [pyrefly](https://pyrefly.org/) for static type checking: pyrefly runs as a pre-commit hook.
- Added a root `index.html` that redirects to the latest docs (`https://zyskarch.github.io/pytestarch/` → `https://zyskarch.github.io/pytestarch/latest/`).
- `from <package> import <module>` is now recognized as an import of `<package>.<module>`, so rules using `are_named` match it ([#145](https://github.com/zyskarch/pytestarch/issues/145)).
- `from .<package> import <module>` is now recognized as an import of `<package>.<module>` as well ([#145](https://github.com/zyskarch/pytestarch/issues/145)).
- The bare relative form `from . import <name>` now also records an import of the containing package itself, matching the absolute `from <package> import <name>` form. Rules naming the package now report the package itself; previously the imported submodule was reported, and for imported attributes and `*` no import was recorded at all. The level-2+ forms behave the same (`from .. import <name>` records the grandparent package).
- A bare relative import whose level exceeds the importer's module hierarchy (such as `from .. import *` in a module without parent packages) now raises an `ImportException` instead of being silently ignored.
- In partial scans (a `module_path` below `root_path`) with `exclude_external_libraries=False`, internal modules outside the scanned `module_path` are no longer added as nodes.
- Overlapping layer definitions, where a module of one layer is a parent or submodule of another layer's module, are now rejected with an `ImproperlyConfigured` error at definition time, instead of a `LayerMismatch` only when rules are applied.
- Symlink aliases are followed during the scan: a module reached through several paths is emitted under each of them, with the target's name only when the walk also reaches the target. Exclusion and `.py`-suffix matching use the walk (link) path, while file content is read from the resolved target. Directory listings and parsed ASTs are cached by resolved path, so aliases are not re-read or re-parsed; symlink cycles terminate.
- Less path resolution during graph construction: only the scan start and symlink entries are resolved, and directory listings and ASTs are reused across aliases.
- Less redundant graph construction work: the per-node and per-edge flatten call, a no-op without a `level_limit`, is skipped, and `add_node` is called without a preceding membership lookup.

### Fixed
- `from . import <name>` no longer turns imported attributes or `*` into imports of non-existent `<package>.<name>` modules.
- Internal modules are no longer added to the graph as spurious external dependency nodes when `exclude_external_libraries=False` (partially fixes [#144](https://github.com/zyskarch/pytestarch/issues/144)).
- Partial scans with `exclude_external_libraries=False` no longer create duplicate bare-name nodes for imports of the scanned module itself (`app` next to the real `src.app`).
- Imports of the scanned module itself are no longer classified as external when `exclude_external_libraries=True`; previously only submodules counted as internal.
- Root and module paths keep the path form the caller passed: anchored (regex) exclusions match again — for the first time also for files — and symlinked roots and module paths keep their link names, so a symlinked `module_path` outside the root builds the graph again instead of crashing.
- Exclusion patterns are matched against forward-slash paths on all platforms, so `src/skipdir`-style patterns work on Windows as well.
- `get_evaluable_architecture` raises a clear error when `root_path` or `module_path` does not exist (dangling symlinks included), instead of silently returning an empty graph in which every rule passes vacuously.
- `get_evaluable_architecture_for_module_objects` raises a clear error when the root or module object has no source file (e.g. namespace or builtin modules), instead of crashing with a `TypeError`.
- Passing `.` as the root keeps the historical quirk of an empty module name prefix (module names such as `.pkg.m`); pass an explicit path for clean names.
- Imports inside `else`, `elif`, `except`, `finally` and `match`/`case` blocks are now recognized. Rules that only passed because these imports were missed can now be violated.
- An importee that starts with the root module name but is not a submodule of it (e.g. `appdirs` for a root module `app`) is no longer misclassified as internal.
- The layer rule now matches modules on exact dot-separated boundaries: `project.model_utils` is no longer treated as part of layer `project.model`, so accesses to it are detected.
- Plot label aliases now apply only to the aliased module and its dot-separated submodules; previously they also relabeled name-prefix matches such as `appdirs` for an alias on `app`.
- `regex_exclusions=None` (the `get_evaluable_architecture` default) is accepted as no exclusions; previously it raised a `TypeError` unless `exclusions` was set.
- Membership checks on the dependency graph raise a `TypeError` for malformed inputs, i.e. anything that is not a module name or a pair of two module names; previously such inputs were silently looked up, producing confusing downstream errors.


## [5.0.0] -- 2026-10-11
### Changed
- Drop support for python 3.9
- Drop support for python 3.10
- Support for python 3.14
- Support for python 3.15
- Increased minimum dependency versions: networkx >=3.6, matplotlib >=3.11
- Accept `pathlib.Path`s in `get_evaluable_architecture(..)`
- Updated development dependencies
- Readme examples and links to documentation
- Documentation is now built with zensical instead of mkdocs

### Fixed
- Straightforward error message when using wildcards in `are_named` rules.
- Typo in docstring of `get_evaluable_architecture(..)`.
- Module filter uses regex when activated instead of only if last module.
- Descriptive error message with actionable guidance when a queried module is not present in the dependency graph.
- Parser no longer errors out on windows due to unspecified encoding.
- Docstring formatting in the API reference: dependency structure examples in the rule assessment docs and the PlantUML arrow operators are now rendered as code.
- Docstring argument mismatches: actual arguments and docstring diverged, so the generated configuration was incomplete.
- `site_url` is configured, so the generated sitemap lists all pages and pages define canonical URLs.

## [4.0.1] -- 2025-08-08
### Fixed
- KeyError when not including all layers with regexes in a Layer rule.

## [4.0.0] -- 2024-04-01
### Changed
- Mechanism of exporting library modules
- Python formatting
- Support for python 3.13

### Fixed
- KeyError when trying to check for imports of submodule by same submodule

## [3.1.1] -- 2024-10-02
### Fixed
- Link to documentation

## [3.1.0] -- 2024-09-16
### Added
- Filter for external dependencies.


## [3.0.1] -- 2024-07-25
### Fixed
- Regex syntax error in newer python versions

## [3.0.0] -- 2024-05-27
### Added
- Support for python 3.12

### Removed
- Support for python 3.8

## [2.0.3] -- 2024-03-17
### Fixed
- Module resolution for nested modules with root and module path mismatch.

## [2.0.2] -- 2024-03-16
### Fixed
- Module resolution for absolute imports when root and module path differ.

## [2.0.1] -- 2024-03-14
### Fixed
- Readme description on module name references.


## [2.0.0] -- 2024-02-23
### Changed
- Matplotlib is no longer installed by default, as it is not required for the core functionality.


## [1.6.0] -- 2024-02-23
### Added
- Support for mypy.

### Changed
- Syntax for example rules in documentation.


## [1.5.1] -- 2023-11-21
### Removed
- Unnecessary dependency.


## [1.5.0] -- 2023-04-12
## Added
- More extensive documentation for the regex matching features.

## [1.4.1] -- 2023-04-09
## Fixed
- Import paths in documentation.

## [1.4.0] -- 2023-04-09
### Added
- Option to specify module names and file exclusions via regex.
- Support for layer architecture.
- Batch support for rule subjects.

### Changed
- Complete module hierarchy present in graph, instead of only for modules that are part of an import dependency.
- Error message only lists violated rule objects when multiple rule objects are defined.

## [1.3.1] -- 2023-01-27
### Changed
- Internal module structure to improve coupling, cohesion.

### Fixed
- Support for python3.8.

## [1.3.0] -- 2022-11-28
### Added
- Reference to modules only by part of their names
- Aliases for plot labels
- Test generation from PUML component diagrams

## [1.2.1] -- 2022-10-21
### Fixed
- Queries with "except itself" excluded too many modules from consideration


## [1.2.0] -- 2022-10-08
### Fixed
- Line separator for rule violation messages


## [1.1.1] -- 2022-10-04
### Fixed
- Line separator for rule violation messages

## [1.1.0] -- 2022-10-02
### Added
- Rule objects can be passed in as a list

### Fixed
- All violations not always returned

## [1.0.3] -- 2022-09-28
### Changed
- Simplified calculation of whether imports are within the project

### Fixed
- Excluded directories no longer searched for parseable files

## [1.0.2] -- 2022-09-28
### Fixed
- All internal modules filtered out if module and root path are not identical and are a sub module of the actual root module.

## [1.0.1] -- 2022-09-27
### Fixed
- Module no longer considered if rule asked only for submodules of a given module

## [1.0.0] -- 2022-09-27
### Changed
- Rename entry point methods for clarity

### Fixed
- Reference to outdated code in documentation

## [0.1.0] -- 2022-09-23
### Added
- More detailed error message for violations of rules checking for absence of imports
- Versioning of documentation

## [0.1.0-alpha.4] -- 2022-09-23
### Added
- Documentation for release of PyTestArch
- More detailed project description

### Changed
- Computation of dependencies between modules on graph

## [0.1.0-alpha.3] -- 2022-09-20
### Fixed
- Different construction of graph node names between OS

## [0.1.0-alpha.1] -- 2022-09-20
### Added
- Documentation
- library MVP
