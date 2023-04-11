from __future__ import annotations

from typing import List

from pytestarch.eval_structure.evaluable_architecture import (
    Module,
    ModuleFilter,
    ModuleGroup,
)
from pytestarch.eval_structure.evaluable_structures import AbstractNode


def to_modules(nodes: List[AbstractNode]) -> List[Module]:
    return list(map(lambda node: Module(name=node), nodes))


def filter_to_module(filter: ModuleFilter) -> Module:
    if filter.parent_module:
        return ModuleGroup(filter.parent_module)

    return Module(filter.name)


def get_node(module_filter: ModuleFilter) -> AbstractNode:
    return module_filter.name or module_filter.parent_module


def get_parent_nodes(module_filters: List[ModuleFilter]) -> List[AbstractNode]:
    result = [module_filter.parent_module for module_filter in module_filters]
    return [node for node in result if node is not None]
