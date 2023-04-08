# Testing your architecture based on PlantUML component diagrams
## General
Instead of hand-crafting a number of rules, you can supply the path to a PlantUML component diagram via a `DiagramRule`. PyTestArch will
then parse this file and generate rules based on the connections of nodes in this diagram. Connections between two nodes
will be converted into 'should only' or 'should' import rules; the absence of a connection will be converted into
'should not' import rules. All rules are then evaluated against an Evaluable.

Currently, parent-child relationships between modules are not supported. This means that for module X and its submodule Y, an edge between them in the diagram
will be interpreted as an 'imports' relationship, not a 'submodule relationship'.

There are two options for naming the components in your diagram:

1) Use their fully qualified name, starting at the root module. For example, in the complex example above, this could be "src.A.fileA" instead of just "fileA" <br>
2) Use only the name of the module itself, for example "fileA". Then you need to supply the prefix left out in the diagrams relative to your root module. In our example,
    this would be "src.A". PyTestArch will then prefix all components in the diagram with this string. <br>


## Supported PlantUML language features
Syntactical requirements for .puml files:
* start of dependency definition needs to be tagged with @startuml
* end of dependency definition needs to be tagged with @enduml
* all text outside these tags is ignored
* component names must be enclosed in square brackets
* exception: if a component as been given an alias via `[module name] as alias`, then the alias should not be wrapped in square brackets
* dependencies must be with either -->, ->, <--, <-, -text->, or <-text-. The dependee is to be placed on the side of the arrow head, the dependor on the opposite side

