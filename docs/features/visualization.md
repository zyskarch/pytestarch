## Visualizing architecture
The graph structure can be plotted with `evaluable_architecture.visualize()` (requires
matplotlib), which plots the dependency graph.
By default, the nodes are labeled with their module name. If a module name is long 
and/or a module has many submodules, the labels may crowd the plot. This can be 
addressed by specifying (short) aliases for the module names by using the keyword argument 
`aliases`. An alias will replace the module name in the label of the respective module
and all its submodules unless the submodule also has an alias, in that case the
submodule's alias takes priority.

## Alias Examples:
Consider an architecture with modules `long_root_name, long_root_name.submodule,
long_root_name.submodule.sub_submodule, long_root_name.other_submodule` then the 
resulting labels for a given aliases are:


| aliases                                                    |  labels                                               |
|------------------------------------------------------------|----------------------------------------------------------------|
| `{'long_root_name': 'r'}`                                   | `r, r.submodule, r.submodule.sub_submodule, r.other_submodule` |
| `{'long_root_name': 'r', 'long_root_name.submodule': 'sub'}` | `r, sub, sub.sub_submodule, r.other_submodule`                 |
