from __future__ import annotations

from pytestarch.eval_structure.evaluable_architecture import Dependency, ModuleFilter
from pytestarch.eval_structure.evaluable_structures import AbstractGraph, AbstractNode
from pytestarch.eval_structure.utils import get_node, get_parent_nodes, to_modules


def get_dependency_between_modules(
    graph: AbstractGraph, dependent: ModuleFilter, dependent_upon: ModuleFilter
) -> list[Dependency]:
    dependent_node = get_node(dependent)
    dependent_upon_nodes = get_all_submodules_of(graph, dependent_upon)

    nodes_to_exclude = get_parent_nodes([dependent, dependent_upon])

    nodes_to_check = [dependent_node]
    checked_nodes = set()

    dependencies = []

    while nodes_to_check:
        node = nodes_to_check.pop()

        if node in checked_nodes:
            continue

        checked_nodes.add(node)

        children = graph.direct_successor_nodes(node)

        for child in children:
            if graph.parent_child_relationship(node, child):
                nodes_to_check.append(child)

            elif (
                child in dependent_upon_nodes
                and node not in nodes_to_exclude
                and child not in nodes_to_exclude
            ):
                dependencies.append(tuple(to_modules([node, child])))
    return dependencies  # type: ignore


def any_dependency_to_module_other_than(  # noqa: C901
    graph: AbstractGraph, dependent: ModuleFilter, dependent_upons: set[ModuleFilter]
) -> list[Dependency]:
    # nodes to exclude are nodes that once reached will not have their submodules analysed next
    nodes_to_exclude = set()
    for dependent_upon in dependent_upons:
        if dependent_upon == dependent:
            continue
        nodes_to_exclude.update(get_all_submodules_of(graph, dependent_upon))

    nodes_fulfilling_criteria = []

    # nodes that count as not fulfilling the criterion are nodes that would technically fulfill the criterion,
    # but have to be excluded for consistency reasons. For example, if the dependent is called A and has two
    # submodules A.X and A.Y. If A.X and A.Y import each other, this would be registered as fulfilling the
    # requirement of a module other than the dependent upons (assuming that A.X and A.Y are not in this list).
    # however, this is not really an import of a module outside A, which is what we are actually looking for

    # should submodules of the dependent module import each other, this does not count as a dependency
    nodes_that_do_not_fulfill_criterion = get_all_submodules_of(graph, dependent)

    if dependent.identifier_is_parent_module:
        # if the parent module is set and has a dependency other than dependent upon, it should not count as only
        # the dependent and its submodules should be considered
        # Example: if we are looking for imports by A.X, we do not care if A itself imports something
        # (but we do care if A.X.M (submodule of A.X) imports something, as this is part of A.X)
        nodes_to_exclude.add(dependent.identifier)

    for dependent_upon in dependent_upons:
        if dependent_upon.identifier_is_parent_module:
            # if there is a dependency to the parent module of dependent upon, this counts, as only dependencies to
            # the true submodules are excluded
            # reason: if something imports B, then it imports something that is not B.X (and B.X is a dependent_upon module)
            # (but we do not care if it imports B.X.M, as this is part of B.X)
            nodes_to_exclude.remove(dependent_upon.identifier)

    nodes_to_check = list(nodes_that_do_not_fulfill_criterion)
    checked_nodes = set()

    while nodes_to_check:
        node = nodes_to_check.pop()

        if node in checked_nodes:
            continue

        if node in nodes_to_exclude:
            continue

        checked_nodes.add(node)

        children = graph.direct_successor_nodes(node)

        for child in children:
            if not graph.parent_child_relationship(node, child):
                if (
                    child not in nodes_to_exclude
                    and child not in nodes_that_do_not_fulfill_criterion
                ):
                    nodes_fulfilling_criteria.append(tuple(to_modules([node, child])))
                else:
                    nodes_to_check.append(child)

    return nodes_fulfilling_criteria  # type: ignore


def any_other_dependency_to_module_than(  # noqa: C901
    graph: AbstractGraph, dependents: set[ModuleFilter], dependent_upon: ModuleFilter
) -> list[Dependency]:
    # submodules of the dependent upon module do not count as an import that is not the dependent upon module
    # submodules of and including the dependent do not count as allowed imports

    # nodes to exclude are nodes that once reached will not have their submodules analysed next
    nodes_to_exclude = set()
    for dependent in dependents:
        if dependent == dependent_upon:
            continue
        nodes_to_exclude.update(get_all_submodules_of(graph, dependent))

    nodes_fulfilling_criteria = []

    # nodes that count as not fulfilling the criterion are nodes that would technically fulfill the criterion,
    # but have to be excluded for consistency reasons. For example, if the dependent upon is called A and has two
    # submodules A.X and A.Y. If A.X and A.Y import each other, this would be registered as fulfilling the
    # requirement of a module other than the dependents (assuming that A.X and A.Y are not in this list).
    # however, this is not really an import by a module outside A, which is what we are actually looking for

    # submodules of the dependent upon do not count as allowed imports e.g. if they import each other
    nodes_that_count_as_not_fulfilling_criterion = get_all_submodules_of(
        graph, dependent_upon
    )

    if dependent_upon.identifier_is_parent_module:
        # if the dependent upon module is defined via a parent module, this parent module is not included in the
        # list of modules that do not fulfill the criteria - only its true submodules are
        # reason: there is a dependency from the parent module to the child module, but this is not an import
        nodes_that_count_as_not_fulfilling_criterion.remove(dependent_upon.identifier)

    nodes_to_check = list(nodes_that_count_as_not_fulfilling_criterion)

    for dependent in dependents:
        if dependent.identifier_is_parent_module:
            # if the dependent module is defined via a parent module, this parent module counts as an allowed import
            # reason: we are looking for dependencies other than module A.X. Parent module A is not (only) A.X, so it counts
            # (submodule A.X.M does not count, as it is not anything else but A.X)
            nodes_to_exclude.remove(dependent.identifier)

    checked_nodes = set()

    while nodes_to_check:
        node = nodes_to_check.pop()

        if node in checked_nodes:
            continue

        checked_nodes.add(node)

        parents = graph.direct_predecessor_nodes(node)

        for parent in parents:
            if not graph.parent_child_relationship(parent, node):
                if (
                    parent not in nodes_to_exclude
                    and parent not in nodes_that_count_as_not_fulfilling_criterion
                ):
                    nodes_fulfilling_criteria.append(tuple(to_modules([parent, node])))

                if parent not in nodes_to_exclude:
                    nodes_to_check.append(parent)

    return nodes_fulfilling_criteria  # type: ignore


def get_all_submodules_of(
    graph: AbstractGraph, module: ModuleFilter
) -> set[AbstractNode]:
    """Returns all submodules of a given module.

    Args:
        module: module to retrieve submodules of

    Returns:
        all submodules, including the module itself
    """
    start_node = get_node(module)

    nodes_to_check = [start_node]
    checked_nodes = set()

    submodules = set()

    while nodes_to_check:
        node = nodes_to_check.pop()

        if node in checked_nodes:
            continue

        checked_nodes.add(node)
        submodules.add(node)

        children = graph.direct_successor_nodes(node)

        for child in children:
            if graph.parent_child_relationship(node, child):
                nodes_to_check.append(child)

    return submodules
