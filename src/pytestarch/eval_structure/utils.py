from __future__ import annotations

from collections.abc import Sequence

from pytestarch.eval_structure.evaluable_architecture import (
    Module,
    ModuleFilter,
    ModuleGroup,
)
from pytestarch.eval_structure.evaluable_structures import AbstractNode


def to_modules(nodes: list[AbstractNode]) -> list[Module]:
    return list(map(lambda node: Module(identifier=node), nodes))


def filter_to_module(filter: ModuleFilter) -> Module:
    if filter.identifier_is_parent_module:
        return ModuleGroup(filter.identifier)

    return Module(filter.identifier)


def get_node(module_filter: ModuleFilter) -> AbstractNode:
    return module_filter.identifier


def get_parent_nodes(module_filters: Sequence[ModuleFilter]) -> list[AbstractNode]:
    result = [
        module_filter.identifier
        for module_filter in module_filters
        if module_filter.identifier_is_parent_module
    ]
    return [node for node in result if node is not None]
