# Changelog

This project uses semantic versioning and follows [keep a changelog](https://keepachangelog.com).

## 4.0.2 TBD
### Fixed
- Straightforward error message when using wildcards in `are_named` rules.

## 4.0.1 -- 2025-08-08
### Fixed
- KeyError when not including all layers with regexes in a Layer rule.

## 4.0.0 -- 2024-04-01
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
