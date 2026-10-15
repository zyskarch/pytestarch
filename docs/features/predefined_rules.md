# Predefined Architecture Rules (experimental)

PyTestArch offers predefined architecture rules in the spirit of ArchUnit's
[predefined rules](https://www.archunit.org/userguide/html/000_Index.html#_architectures).
They encapsulate a common architectural style on top of the regular
[layer architecture rules](layer_architecture_checks.md), so that the style can be enforced without
defining each layer and dependency direction by hand.

⚠ These rules are still drafts: their API is not finalized yet. They therefore live in the
`pytestarch.experimental` module, which may change or be removed without notice. Feedback and
suggestions are welcome - create a new [issue](https://github.com/zyskarch/pytestarch/issues/new).

## Layered Architecture rules

The generic layered architecture check enforces a whitelist per layer: each of the named layers may only access the
layers listed as its allowed dependencies. It shares the layer rule engine with the Onion Architecture rule below, but
unlike it can be used to detect any layered style directly, e.g. a typical controller - service - persistence layering:

```python
from pytestarch import get_evaluable_architecture
from pytestarch.experimental import layered_architecture


rules = layered_architecture(
    layers={
        "controller": "my_project.controller",
        "service": "my_project.service",
        "persistence": "my_project.persistence",
        "model": "my_project.model",
    },
    allowed_dependencies={
        "controller": ["service"],
        "service": ["persistence", "model"],
        "persistence": ["model"],
    },
)

evaluable = get_evaluable_architecture(root_path, module_path)
rules.assert_applies(evaluable)
```

Each entry of `allowed_dependencies` generates one rule enforcing that the layer may only access the listed layers;
an empty list means the layer must not access anything, and layers omitted from `allowed_dependencies` are defined
but unrestricted.

Notes:

* A layer listed in `allowed_dependencies` with an **empty list** must not access any
  other configured layer.
* Layers that appear in `layers` but are omitted from `allowed_dependencies` are
  *defined* (so they can be named as allowed targets) but have no rule generated for
  them.
* Referencing an undefined layer name in `allowed_dependencies` (as subject or target)
  raises `ImproperlyConfigured` immediately, before any evaluation takes place.
- Dependencies within a layer are always allowed.


## Onion Architecture rule

The Onion Architecture check verifies who may access each component: the domain models may only be accessed by the
domain services, application services, and adapters, the domain services only by the application services and
adapters, and the application services only by adapters. Nothing outside these components may access any of them,
and adapters in particular must not be accessed by anyone.

Each component is mapped to one or more modules:

```python
from pytestarch import get_evaluable_architecture
from pytestarch.experimental import onion_architecture

rule = (
    onion_architecture()
    .domain_models("my_project.domain.model")
    .domain_services("my_project.domain.service")
    .application_services("my_project.application")
    .adapter("cli", "my_project.adapter.cli")
    .adapter("rest", ["my_project.adapter.rest", "my_project.adapter.grpc"])
)

evaluable = get_evaluable_architecture(root_path, module_path)
rule.assert_applies(evaluable)
```

Notes:

- All components are optional, but at least one must be specified.
  Any skipped component simply does not contribute to the access restrictions.
- The rule does not restrict which modules a component itself imports - only who is allowed to access it.
- Dependencies between modules of the same component are always allowed.
- Misconfigurations - a component specified more than once, a component without modules, or a module assigned to
  more than one component - are rejected with an `ImproperlyConfigured`.
- For architecture styles that are not covered by this rule, the more generic
  [`layered_architecture` rule](#layered-architecture-rules) (see above) can be used instead.
