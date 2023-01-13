from __future__ import annotations

from typing import List

from pytestarch.eval_structure.evaluable_architecture import Module
from pytestarch.eval_structure.evaluable_structures import AbstractNode


def to_modules(nodes: List[AbstractNode]) -> List[Module]:
    return list(map(lambda node: Module(name=node), nodes))


def get_node(dependent: Module) -> AbstractNode:
    return dependent.name or dependent.parent_module


def get_excluded_nodes(modules: List[Module]) -> List[AbstractNode]:
    result = [module.parent_module for module in modules]
    return [node for node in result if node is not None]
