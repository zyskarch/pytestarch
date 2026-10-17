# General Concept
PyTestArch creates an Abstract Syntax Tree for each Python file it scans. It then extracts only the information about 
module imports from the AST and converts them to an internal representation. This is currently a graph supplied by the 
[NetworkX](https://networkx.org/) library.

When the user defines a rule and evaluates the internal representation against it, the rule is converted into a set of
graph operations that are then carried out on the previously generated graph.

## Generating the evaluable architecture representation
When scanning and processing the requested modules, PyTestArch executes the following step:
1) Parse all files starting at the requested `module_path`. This only takes python source files into account that are not explicitly excluded.

2) Convert the generated AST into custom dependency representations. In this step, it is ensured that all internal modules (either importing or imported) receive their fully 
qualified name.

3) Generate a list of all modules that were parsed. This list is used to differentiate between external and internal dependencies (external dependencies will not have been parsed).

4) If not requested otherwise, external dependencies will be filtered out.

5) If external dependencies should be included, they will be added to the list of modules.

6) The dependency representations are converted to a graph structure.


## Simple Example

### Parsing all files
Consider the following project structure:
```
my_project/
    src/
        main.py
        util.py
        util_test.py
```

Both `main.py` and `util_test.py` are importing a util function defined in `util.py`; no other imports exist.

With "my_project" as the project's root folder and "src" as the folder to evaluate, this will create the following graph:

![Simple Example Graph](../resources/docu_simple_example.png)

Each module has a direct path to all submodules, in this case: "src" is connected to all three modules it contains, 
"src.main", "src.util", and "src.util_test".

In addition, a module that imports another module has a directed edge linking it to this module. For example, "src.main"
imports "src.util" and therefore the graph has an edge connecting these modules, with the arrow head pointing at the imported
module, in this case "src.util".

### Excluding some files

In the example above, the `util_test.py` file is included in the graph and will be considered when evaluating the architecture.
If certain files should be excluded from the analysis, this can be done by specifying an exclusion pattern. In our example,
if we want to exclude `util_test.py`, we could use:
```python
from pytestarch import get_evaluable_architecture

evaluable = get_evaluable_architecture(
    "/home/my_project",
    "/home/my_project/src",
    exclusions=(),
    regex_exclusions=(r".*_test\.py",),
)
```
This will exclude all files with names ending in "_test.py". It is also possible to exclude directories.


## More complex example
As a basis for describing the query language, let's consider a more complex example:
```
/test_project
    /src
       __init__.py
       /A
            __init__.py
            fileA.py
            /A1
                __init__.py
                fileA1.py
                fileA1_b.py
                /A11
                    __init__.py
                    fileA11.py
            /A2
                __init__.py
                fileA2.py
       /B
            __init__.py
            fileB.py
            /B1
                __init__.py
                fileB1.py
                fileB2.py
       /C 
            __init__.py
            fileC.py
```

With the following list of imports:
<ul>
    <li>fileA imports fileC</li>
    <li>fileA11 imports fileB1</li>
    <li>fileA2 imports fileC</li>
    <li>fileB imports fileA11</li>
    <li>fileB2 imports fileA11</li>
    <li>fileC imports the built-in os module</li>
</ul>

This creates the following graph (excluding all `__init__.py`):

![Complex Example](../resources/docu_complex_example.png)

Note that the module names in the diagram have been abbreviated: For example, the node "fileA" is actually named "src.A.fileA".

Most of the edges in this graph are due to parent-child relationships between the modules. However, five of the six import
relationships defined above are present in the graph - only fileC has no connection to an "os" node; in fact, there is no
node names "os" at all.

This has been achieved by setting the `exclude_external_libraries` flag in the `get_evaluable_architecture` function. All modules that 
not located hierarchically below the root path, in this case "test_project", will be excluded from the graph.

### Module not found in graph
If a rule references a module that does not appear in the dependency graph, PyTestArch raises a `ModuleUnknown` error with an actionable message. Common causes are:

- **External library excluded**: the module belongs to a third-party package and `exclude_external_libraries=True` (the default). Pass `exclude_external_libraries=False` to `get_evaluable_architecture()` to include it.
- **Module never imported**: the module exists but is not imported by any code under the scanned `module_path`, so it was never added to the graph.
- **Misspelled module name**: module names in rules must match the fully qualified import name (e.g. `mypackage.service`, not `service`).


<br>
# Additional Notes
## root_path vs. module_path in get_evaluable_architecture
The `root_path` should point towards the most top level module. In the example above, this would be `src` - not `test_project`,
as `test_project` is not the top level code directory.
The `module_path` is the module where the dependency scan will start. It has to be either identical to `root_path` or 
a submodule of it.

`root_path` is treated in one of two ways, depending on whether it contains an `__init__.py`:

- **Package root**: if `root_path` contains an `__init__.py`, it is a Python module itself. All module names are prefixed
  with its name (e.g. a root of `.../src` with `.../src/__init__.py` yields names such as `src.moduleA.fileA`), and it is
  the common ancestor of all internal modules.
- **Container root**: if `root_path` contains no `__init__.py` (e.g. a plain `src` directory that holds several
  top-level packages next to each other), it is treated as a pure container directory. By default, module names are still
  prefixed with the root directory's name (e.g. `src.packageA.moduleA`), keeping the module names consistent with the
  module paths used before container-support existed. Rules refer to these modules by their prefixed names, e.g.
  `Rule().modules_that().are_named("src.packageB")...`.

  Imports that are written root-relative (e.g. `from packageB import moduleB` inside `packageA`, with the import
  resolving against the packages below `src`) are classified as internal dependencies and resolved to their
  prefixed names (`src.packageA.moduleA` imports `src.packageB`), so no spurious duplicate nodes appear next to the
  prefixed modules.

  With the opt-in parameter `module_naming="relative"`, module names are instead derived relative to the root directory
  without any prefix (e.g. `packageA.moduleA`), and root-relative imports resolve against the packages below the root,
  e.g. `Rule().modules_that().are_named("packageB")...`. As with the default naming, imports of packages that lie
  outside a partial scan's `module_path` are listed as external dependencies under their bare names. The option has no
  effect for package roots, as their name is the real package name there and always prefixes the module names.

**Namespace packages**: a PEP 420 namespace package root (a package directory without `__init__.py`) is indistinguishable
from a container root. Module names keep the root directory prefix by default; pass `module_naming="relative"` to derive
the names relative to the root without the prefix. In `relative` mode, imports must be written relative to the top-level
packages below the root.

With `module_naming="relative"`, an import that shares its top-level name with a scanned module is treated as
internal - mirroring Python's own `sys.path` behavior, where a local package shadows a third-party library with the
same name.


## Module names
In all rules, modules have to be referred to by their fully qualified name, meaning relative to the `root_path` - not the
`module_path`! This helps to distinguish between internal and external modules.
