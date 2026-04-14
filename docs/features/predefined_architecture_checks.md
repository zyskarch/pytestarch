# Predefined Architecture Rules

PyTestArch ships with convenience helpers for three common architectural patterns so that
you do not have to hand-craft `LayeredArchitecture` + `LayerRule` objects from scratch.
All three helpers return a `MultipleRuleApplier` (or, for `HexagonalArchitecture`, expose
an `assert_applies` method directly) and internally delegate to the same layer-rule engine
described in [Layer Architecture Dependency Rules](layer_architecture_checks.md).


## Layered Architecture

`layered_architecture()` is the generic building block.  It accepts an arbitrary number of
named layers and a mapping that declares which layers each layer is allowed to access.

```python
from pytestarch import layered_architecture, get_evaluable_architecture

evaluable = get_evaluable_architecture(root_path, module_path)

rules = layered_architecture(
    layers={
        "presentation": "my_project.presentation",
        "application":  "my_project.application",
        "domain":       ["my_project.domain.models", "my_project.domain.services"],
        "infrastructure": "my_project.infrastructure",
    },
    allowed_dependencies={
        "presentation":   ["application"],
        "application":    ["domain"],
        "domain":         [],                         # innermost – no outward access
        "infrastructure": ["domain", "application"],  # may call inward layers
    },
)

rules.assert_applies(evaluable)
```

* A layer listed in `allowed_dependencies` with an **empty list** must not access any
  other configured layer.
* Layers that appear in `layers` but are omitted from `allowed_dependencies` are
  *defined* (so they can be named as allowed targets) but have no rule generated for
  them.
* Referencing an undefined layer name in `allowed_dependencies` (as subject or target)
  raises `ImproperlyConfigured` immediately, before any evaluation takes place.


## Onion Architecture

`onion_architecture()` is a three-layer preset that follows the standard onion / clean
architecture dependency rules:

| Layer          | May access                    |
|----------------|-------------------------------|
| domain         | nothing                       |
| application    | domain only                   |
| infrastructure | domain **and** application    |

```python
from pytestarch import onion_architecture, get_evaluable_architecture

evaluable = get_evaluable_architecture(root_path, module_path)

onion_architecture(
    domain_layer=["my_project.domain.models", "my_project.domain.services"],
    application_layer="my_project.application",
    infrastructure_layer="my_project.infrastructure",
).assert_applies(evaluable)
```

Each parameter accepts either a single module name (string) or a list of module names.


## Hexagonal Architecture

`HexagonalArchitecture` is a builder that follows ArchUnit's hexagonal (ports and
adapters) model.  It recognises four kinds of layer:

| Layer                | Allowed to access                                          |
|----------------------|------------------------------------------------------------|
| `domain_models`      | nothing                                                    |
| `domain_services`    | domain models                                              |
| `application_services` | domain models, domain services                           |
| adapter (any name)   | domain models, domain services, application services       |

Only layers that are **explicitly configured** participate in the rule set; you may
configure as few or as many as your project uses.  Any number of named adapters can be
added.

```python
from pytestarch import HexagonalArchitecture, get_evaluable_architecture

evaluable = get_evaluable_architecture(root_path, module_path)

(
    HexagonalArchitecture()
    .domain_models("my_project.domain.models")
    .domain_services("my_project.domain.services")
    .application_services("my_project.application")
    .adapter("rest", "my_project.adapters.rest")
    .adapter("db",   "my_project.adapters.db")
    .assert_applies(evaluable)
)
```

Each builder method returns `self`, so calls can be chained freely.  Calling
`adapter(name)` without at least one module name raises `ImproperlyConfigured`.

### Partial configurations

If a layer type is not relevant to your project you can simply omit it.  For example, a
project without a distinct domain-services layer:

```python
(
    HexagonalArchitecture()
    .domain_models("my_project.models")
    .application_services("my_project.application")
    .adapter("cli", "my_project.cli")
    .assert_applies(evaluable)
)
```
