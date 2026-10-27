# Changelog

This project uses semantic versioning and follows [keep a changelog](https://keepachangelog.com).

## [TBD] -- Unreleased
### Added
- Explicit multi-module support through the keyword-only `mode="multi_module"` option on both architecture entry points. The default `mode="legacy"` preserves historical directory-prefixed names and does not enable multi-package or monorepo import resolution. Naming and resolution are selected together, without a separate naming option.
- In multi-module mode, container root directories (a `root_path` without `__init__.py`, e.g. a plain `src` folder holding several top-level packages) use names relative to the root (`package1.module1`) and resolve imports between those packages. Package roots retain their package-name prefix. Packages outside a partial scan's `module_path` remain external (fixes [#144](https://github.com/zyskarch/pytestarch/issues/144)).
- With `mode="multi_module"`, `get_evaluable_architecture_for_module_objects()` accepts any iterable (list, tuple, set, ...) of sibling top-level packages and always uses full import names, including namespace parents. One root keeps the same names whether passed directly, wrapped in an iterable, or alongside another root. Iterable roots require explicit opt-in. `module` is optional and defaults to all roots. Namespace packages and packages spread over several directories are rejected as root objects; iterable subpackages of a concrete parent package are also rejected. Multi-root scans reject packages whose import name does not match their directory name, because names are derived from paths.
- `module_path` of `get_evaluable_architecture()` is optional and defaults to `root_path`, so `get_evaluable_architecture(root)` scans everything below the root. It may also point to a Python file.
- Multi-module mode resolves absolute imports against import roots. Every direct child directory that holds top-level packages or standalone modules is a local root for code in the same project; conventional `src` directories directly beneath the scan root, direct child projects with a `pyproject.toml`, `setup.py` or `setup.cfg`, and the scan root itself may also provide packages to other projects. A child project's own `src` folder requires a project marker or explicit `import_roots` to provide packages across projects. The importer's own root wins, followed by exactly one other provider; several providers stay ambiguous. Provider discovery is file-system based and independent of exclusions and partial scans, so names keep project directories and same-named packages remain separate. Only direct child directories and their `src` folders are discovered automatically; deeper or unmarked layouts can be declared with the new `import_roots` option.
- `import_roots` on `get_evaluable_architecture()` declares the directories that define import prefixes and may provide packages to other projects. It replaces automatic cross-project discovery, requires `mode="multi_module"` and a container root, and keeps local roots available. An empty `import_roots=()` disables all automatic cross-project providers, including the scan root itself, while imports within the same scope keep resolving; listing the scan root explicitly (`"."`) re-enables its cross-project role. Each listed root is scoped to its enclosing project when it is a `src` folder and to its own directory otherwise, so `import_roots=("libs/svc_a/src", "libs/svc_b/src")` declares two separate scopes and same-named packages in them stay distinct. A listed root may also hold standalone top-level `.py` modules instead of packages: a source root containing only `main.py` is accepted and provides the module `main`.

### Changed
- Default legacy mode keeps its module names, but graph results can change because of the import fixes below (`from <package> import <module>`, bare relative imports, conditional blocks, self-imports, partial scans). Review rules that depend on those imports after upgrading.
- Opting into multi-module mode can reveal dependencies that legacy scans classified as external. Rules must use the mode's root-relative path names or full module-object import names. Legacy mode retains directory-prefixed names and bare external import nodes.
- Passing `.` (or `/`) as `root_path` no longer yields module names with an empty name prefix (historically `.pkg.m`); module names come out clean, e.g. `pkg.mod`.

### Fixed
- Import providers are discovered from the file system instead of the scanned module set. Excluding a package, or scanning only part of the tree, no longer redirects its imports to another project or resolves an otherwise ambiguous import. Excluded modules remain outside the scanned graph.
- Packages in arbitrary unmarked directories such as `docs/`, `tests/` or `scripts/` no longer satisfy imports from other projects merely because they exist below the scan root. They remain local roots for code in the same scope; cross-project providers include conventional `src` roots directly beneath the scan root, marked projects or explicit `import_roots`.
- Unresolved imports (no import-root provider for the top-level name, several providers, or a selected provider whose resolved module is missing from or excluded by the scan) keep the name as written and are never matched against another project's same-named package. Because graph nodes are plain strings, such an import is omitted from the graph when its bare name, or the name of one of its parents, equals an internal node (including implicit parent nodes), even with `exclude_external_libraries=False`; other unresolved imports can be retained as bare-named external nodes.
- `module_path` outside the root and invalid `import_roots` entries are rejected with actionable messages.
- A `module_path` pointing to a Python file now derives the module name without the `.py` suffix and keeps internal-module detection consistent.
- A dotted root directory (e.g. `x.v1`) now receives the same `level_limit` adjustment as a dotted module-object root.
- `exclusions=()` now disables the default `__pycache__` exclusion instead of raising a `TypeError`.
- Monorepo imports select the top-level package provider before resolving submodules. Missing children no longer resolve into another project's same-named package, and a unique child does not disambiguate multiple package providers.
- Monorepo layout discovery no longer depends on scan exclusions: excluding other projects preserves import resolution and rule checks within retained projects. Excluded modules remain outside the scanned graph.
- In multi-module mode, `level_limit=1` on a container root retains only top-level packages; `level_limit=0` is rejected with `ImproperlyConfigured` when scanning the container itself because it is not a module. Legacy mode keeps the directory-name prefix as a hierarchy level.
- In multi-module mode, a relative import in a module located directly at a container root (no `__init__.py`) raises an explanatory `ImportException`. In legacy mode it resolves against the root directory's name.

## [5.1.1] -- 2026-11-08
### Changed
- In a container root (a `root_path` directory without `__init__.py`, e.g. `src`), imports between top-level packages are now classified as internal. Forbidding rules over them that previously passed vacuously may now fail; rules and `external_exclusions` must use the prefixed names (`src.package2` instead of `package2`).

### Fixed
- Absolute imports written root-relative to the scan root (e.g. `from package2 import module2` below a `src` root) are now resolved to their prefixed module names (`src.package2.module2`) instead of staying external (partially fixes [#144](https://github.com/zyskarch/pytestarch/issues/144); module naming is unchanged). Partial scans and package roots (with `__init__.py`) are unaffected. A top-level internal module sharing its name with an external library (`src/logging` vs `logging`) takes precedence.

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
