# Checking dependencies between layers in a layered architecture

## Why are new rule types needed?
Sometimes, rules do not concern individual modules, but entire layers of an application, which in turn contains one or 
more modules. 
The module dependency check methods can of course also be used here, but often they may not be sufficient. Consider an
example project with three modules (M, N, O). M imports O, but N does not import anything. M and N belong to one layer -
let's call it 'import', O belongs to another layer called 'model'. The 'import' layer is expected to import the 'model' 
layer, but not vice versa.

Using the module dependency query language as described in [Module Dependency Rules](module_import_checks.md), this 
expected import behavior would be difficult to specify, as a rule like 

```
Rule() \
    .modules_that()\ 
    .are_named(["M", "N"]) \
    .should() \
    .import_modules_that() \
    .are_named("O")
```

would require *both* M and N to import O.


## Layer architecture rules
Instead, one can use the layer architecture rules. Using this type of rule has two steps: defining a layered 
architecture, and then defining a rule based on it.

### Layered architecture
The LayeredArchitecture object should be used to group modules into layers. Not all modules have to belong to a layer
(for more details on how this influences layer rules, see below). A layered architecture can be defined like this:
```
arch = LayeredArchitecture() \
            .layer("import") \
            .containing_modules(["M", "N"]) \
            .layer("model") \
            .containing_modules("O")
```
In this layered architecture, the modules M and N belong to layer 'import'; while module O belongs to layer 'model'.


⚠ Note that PyTestArch assumes that all submodules of a module belong to the same layer as their parent module!


### Layer rules
After defining a layered architecture, layer rules can not be defined based on it. Using the `arch` object defined
above, the dependency rule that could not properly be defined in the regular syntax can then be defined as:
```
rule = LayerRule() \
            .based_on(arch). \  # needs to be passed in first
            .layers_that() \
            .are_named("import") \
            .should_only() \
            .access_layers_that() \
            .are_named("model")
```
All modules within one layer are treated as one entity. This means that this rule will apply to an evaluable
architecture, as long either module M or module N imports module O, and neither imports anything else.
This means that for rules that require no dependency between layers, no module of these layers can import another module
of these layers. However, for rules that only require one dependency to be present, it is sufficient if there is one 
dependency between one module from one layer and one module from the other layer.


Note that the "import" verb markers of the module dependency rules are replaced by "access" here, to mark the difference
between these rule types and also to be more in line with ArchUnit's syntax.


Not all modules need to belong to layers,
but then no layer architecture rules can be specified for them. They will however be considered when evaluating whether 
a layer architecture rules applies. For example, module M of layer A imports module N from layer B and module O, which 
is not part of any layer. A rule like
```
LayerRule().based_on(arch).layers_that().are_named("A").should_only().access_layers_that().are_named("B")
```
would raise an AssertionException, as module M also imports module O.


For an explanation of the meaning of the different verb markers used (e.g. should, except) refer to 
[Module Dependency Rules](module_import_checks.md). The two types of query syntax differ in the following points:
1) "import" is replaced by "access"
2) Only "are_named" rule subject and object specifications are allowed
3) The layer architecture rules need to be started by passing in the layered architecture object that contains the layer 
definitions.