"""Base class for different graph implementations of an evaluable structure. Delegates direct access to graph nodes
and edges to its subclasses in a template pattern.
"""
from collections import defaultdict
from itertools import product
from typing import Any, List, Set, Union, Iterable

from pytestarch.eval_structure.evaluable_architecture import (
    EvaluableArchitecture,
    LaxDependenciesByBaseModule,
    Module,
    StrictDependenciesByBaseModules,
    StrictDependency,
)
from pytestarch.eval_structure.evaluable_structures import AbstractGraph, AbstractNode
from pytestarch.exceptions import ImpossibleMatch

ALL_MARKER = "*"


class EvaluableArchitectureGraph(EvaluableArchitecture):
    """Abstract implementation of an evaluable object that is based on a graph structure."""

    def __init__(self, graph: AbstractGraph) -> None:
        self._graph = graph

    def get_dependencies(
        self,
        dependents: Union[Module, List[Module]],
        dependent_upons: Union[Module, List[Module]],
    ) -> StrictDependenciesByBaseModules:
        result = {}

        dependents = self._listify(dependents)
        dependent_upons = self._listify(dependent_upons)

        dependents, dependent_upons = self._convert_to_full_name_matches(
            [dependents, dependent_upons]
        )

        for dependent, dependent_upon in product(dependents, dependent_upons):
            dependency = self._get_dependency_between_modules(dependent, dependent_upon)
            result[(dependent, dependent_upon)] = dependency

        return result

    def _get_dependency_between_modules(
        self, dependent: Module, dependent_upon: Module
    ) -> List[StrictDependency]:
        dependent_node = self._get_node(dependent)
        dependent_upon_nodes = self._get_all_submodules_of(dependent_upon)

        nodes_to_exclude = self._get_excluded_nodes([dependent, dependent_upon])

        nodes_to_check = [dependent_node]
        checked_nodes = set()

        dependencies = []

        while nodes_to_check:
            node = nodes_to_check.pop()

            if node in checked_nodes:
                continue

            checked_nodes.add(node)

            children = self._graph.direct_successor_nodes(node)

            for child in children:
                if self._graph.parent_child_relationship(node, child):
                    nodes_to_check.append(child)

                elif (
                    child in dependent_upon_nodes
                    and node not in nodes_to_exclude
                    and child not in nodes_to_exclude
                ):
                    dependencies.append(tuple(self._to_modules([node, child])))
        return dependencies  # type: ignore

    def _get_node(self, dependent: Module) -> AbstractNode:
        return dependent.name or dependent.parent_module

    def any_dependencies_to_modules_other_than(
        self,
        dependents: Union[Module, List[Module]],
        dependent_upons: Union[Module, List[Module]],
    ) -> LaxDependenciesByBaseModule:
        result = {}

        dependents = self._listify(dependents)
        dependent_upons = self._listify(dependent_upons)

        dependents, dependent_upons = self._convert_to_full_name_matches(
            [dependents, dependent_upons]
        )

        for dependent in dependents:
            dependencies = self._any_dependency_to_module_other_than(
                dependent, dependent_upons
            )
            result[dependent] = dependencies

        return result

    def _listify(self, module: Union[Module, List[Module]]) -> List[Module]:
        return [module] if not isinstance(module, list) else module

    def _any_dependency_to_module_other_than(  # noqa: C901
        self, dependent: Module, dependent_upons: List[Module]
    ) -> List[StrictDependency]:
        # nodes to exclude are nodes that once reached will not have their submodules analysed next
        nodes_to_exclude = set()
        for dependent_upon in dependent_upons:
            if dependent_upon == dependent:
                continue
            nodes_to_exclude.update(self._get_all_submodules_of(dependent_upon))

        nodes_fulfilling_criteria = []

        # nodes that count as not fulfilling the criterion are nodes that would technically fulfill the criterion,
        # but have to be excluded for consistency reasons. For example, if the dependent is called A and has two
        # submodules A.X and A.Y. If A.X and A.Y import each other, this would be registered as fulfilling the
        # requirement of a module other than the dependent upons (assuming that A.X and A.Y are not in this list).
        # however, this is not really an import of a module outside A, which is what we are actually looking for

        # should submodules of the dependent module import each other, this does not count as a dependency
        nodes_that_do_not_fulfill_criterion = self._get_all_submodules_of(dependent)

        if dependent.parent_module is not None:
            # if the parent module is set and has a dependency other than dependent upon, it should not count as only
            # the dependent and its submodules should be considered
            # Example: if we are looking for imports by A.X, we do not care if A itself imports something
            # (but we do care if A.X.M (submodule of A.X) imports something, as this is part of A.X)
            nodes_to_exclude.add(dependent.parent_module)

        for dependent_upon in dependent_upons:
            if dependent_upon.parent_module is not None:
                # if there is a dependency to the parent module of dependent upon, this counts, as only dependencies to
                # the true submodules are excluded
                # reason: if something imports B, then it imports something that is not B.X (and B.X is a dependent_upon module)
                # (but we do not care if it imports B.X.M, as this is part of B.X)
                nodes_to_exclude.remove(dependent_upon.parent_module)

        nodes_to_check = list(nodes_that_do_not_fulfill_criterion)
        checked_nodes = set()

        while nodes_to_check:
            node = nodes_to_check.pop()

            if node in checked_nodes:
                continue

            if node in nodes_to_exclude:
                continue

            checked_nodes.add(node)

            children = self._graph.direct_successor_nodes(node)

            for child in children:

                if not self._graph.parent_child_relationship(node, child):
                    if (
                        child not in nodes_to_exclude
                        and child not in nodes_that_do_not_fulfill_criterion
                    ):
                        nodes_fulfilling_criteria.append(
                            tuple(self._to_modules([node, child]))
                        )
                    else:
                        nodes_to_check.append(child)

        return nodes_fulfilling_criteria  # type: ignore

    def any_other_dependencies_to_modules_than(
        self,
        dependents: Union[Module, List[Module]],
        dependent_upons: Union[Module, List[Module]],
    ) -> LaxDependenciesByBaseModule:
        result = {}

        dependents = self._listify(dependents)
        dependent_upons = self._listify(dependent_upons)

        dependents, dependent_upons = self._convert_to_full_name_matches(
            [dependents, dependent_upons]
        )

        for dependent_upon in dependent_upons:
            dependencies = self._any_other_dependency_to_module_than(
                dependents, dependent_upon
            )
            result[dependent_upon] = dependencies

        return result

    def _any_other_dependency_to_module_than(  # noqa: C901
        self, dependents: List[Module], dependent_upon: Module
    ) -> List[StrictDependency]:
        # submodules of the dependent upon module do not count as an import that is not the dependent upon module
        # submodules of and including the dependent do not count as allowed imports

        # nodes to exclude are nodes that once reached will not have their submodules analysed next
        nodes_to_exclude = set()
        for dependent in dependents:
            if dependent == dependent_upon:
                continue
            nodes_to_exclude.update(self._get_all_submodules_of(dependent))

        nodes_fulfilling_criteria = []

        # nodes that count as not fulfilling the criterion are nodes that would technically fulfill the criterion,
        # but have to be excluded for consistency reasons. For example, if the dependent upon is called A and has two
        # submodules A.X and A.Y. If A.X and A.Y import each other, this would be registered as fulfilling the
        # requirement of a module other than the dependents (assuming that A.X and A.Y are not in this list).
        # however, this is not really an import by a module outside A, which is what we are actually looking for

        # submodules of the dependent upon do not count as allowed imports e.g. if they import each other
        nodes_that_count_as_not_fulfilling_criterion = self._get_all_submodules_of(
            dependent_upon
        )

        if dependent_upon.parent_module is not None:
            # if the dependent upon module is defined via a parent module, this parent module is not included in the
            # list of modules that do not fulfill the criteria - only its true submodules are
            # reason: there is a dependency from the parent module to the child module, but this is not an import
            nodes_that_count_as_not_fulfilling_criterion.remove(
                dependent_upon.parent_module
            )

        nodes_to_check = list(nodes_that_count_as_not_fulfilling_criterion)

        for dependent in dependents:
            if dependent.parent_module is not None:
                # if the dependent module is defined via a parent module, this parent module counts as an allowed import
                # reason: we are looking for dependencies other than module A.X. Parent module A is not (only) A.X, so it counts
                # (submodule A.X.M does not count, as it is not anything else but A.X)
                nodes_to_exclude.remove(dependent.parent_module)

        checked_nodes = set()

        while nodes_to_check:
            node = nodes_to_check.pop()

            if node in checked_nodes:
                continue

            checked_nodes.add(node)

            parents = self._graph.direct_predecessor_nodes(node)

            for parent in parents:

                if not self._graph.parent_child_relationship(parent, node):
                    if (
                        parent not in nodes_to_exclude
                        and parent not in nodes_that_count_as_not_fulfilling_criterion
                    ):
                        nodes_fulfilling_criteria.append(
                            tuple(self._to_modules([parent, node]))
                        )

                    if parent not in nodes_to_exclude:
                        nodes_to_check.append(parent)

        return nodes_fulfilling_criteria  # type: ignore

    @classmethod
    def _to_modules(cls, nodes: List[AbstractNode]) -> List[Module]:
        return list(map(lambda node: Module(name=node), nodes))

    def _get_all_submodules_of(self, module: Module) -> Set[AbstractNode]:
        """Returns all submodules of a given module.

        Args:
            module: module to retrieve submodules of

        Returns:
            all submodules, including the module itself
        """
        start_node = self._get_node(module)

        nodes_to_check = [start_node]
        checked_nodes = set()

        submodules = set()

        while nodes_to_check:
            node = nodes_to_check.pop()

            if node in checked_nodes:
                continue

            checked_nodes.add(node)
            submodules.add(node)

            children = self._graph.direct_successor_nodes(node)

            for child in children:
                if self._graph.parent_child_relationship(node, child):
                    nodes_to_check.append(child)

        return submodules

    def visualize(self, **kwargs: Any) -> None:
        self._graph.draw(**kwargs)

    @classmethod
    def _get_excluded_nodes(cls, modules: List[Module]) -> List[AbstractNode]:
        result = [module.parent_module for module in modules]
        return [node for node in result if node is not None]

    def _convert_to_full_name_matches(
        self, module_groups: List[List[Module]]
    ) -> List[List[Module]]:
        """For each module requiring a partial name match, find all modules that match.
        Modules without the partial name match requirement are appended to the output as-is.

        To avoid iterating over all modules in the graph multiple times, multiple different lists of modules to match
        can be passed in. A list of identical length will be returned: Each module in input list with idx n will
        also be present (either directly, if no partial match; or replaced by its match) in list with idx n in the
        output.
        """

        modules_by_group = {idx: group for idx, group in enumerate(module_groups)}

        (
            partial_match_module_name_by_group,
            result_by_group,
        ) = self._split_into_complete_modules_and_partial_matches(modules_by_group)

        if not any(partial_match_module_name_by_group.values()):
            return self._convert_dict_values_to_list_sorted_by_keys(result_by_group)

        matched_module_names_by_group = defaultdict(set)

        never_matched = {
            module
            for modules in partial_match_module_name_by_group.values()
            for module in modules
        }

        for node in self._graph.nodes:
            for group, matches in partial_match_module_name_by_group.items():
                matched = False

                for match in matches:
                    if matched and match not in never_matched:
                        continue

                    if self._partial_name_match(match, node):
                        matched_module_names_by_group[group].add(node)

                        if match in never_matched:
                            never_matched.remove(match)

        if never_matched:
            raise ImpossibleMatch(
                f'No modules found that match: {", ".join(never_matched)}'
            )

        for group, matched_module_names in matched_module_names_by_group.items():
            result_by_group[group].extend(
                self._convert_to_modules(matched_module_names)
            )

        return self._convert_dict_values_to_list_sorted_by_keys(result_by_group)

    def _split_into_complete_modules_and_partial_matches(
        self,
        modules_by_group: dict[int, List[Any]],
    ) -> tuple[dict[int, List[AbstractNode]], dict[int, List[Module]]]:
        result_by_group: dict[int, List[Module]] = defaultdict(list)
        partial_match_module_name_by_group: dict[int, List[AbstractNode]] = {}

        for group, modules in modules_by_group.items():
            partial_match_module_names = []
            result = []

            for node in modules:
                partial_match_module_names.append(
                    self._get_node(node)
                ) if node.partial_match else result.append(node)

            result_by_group[group] = result
            partial_match_module_name_by_group[group] = partial_match_module_names

        return partial_match_module_name_by_group, result_by_group

    @classmethod
    def _convert_dict_values_to_list_sorted_by_keys(
        cls, d: dict[Any, Iterable[Any]]
    ) -> List[List[Any]]:
        return [group_and_values[1] for group_and_values in sorted(d.items())]

    @classmethod
    def _partial_name_match(cls, module_to_match: str, name: AbstractNode) -> bool:
        starts_with_all_marker = module_to_match.startswith(ALL_MARKER)
        ends_with_al_marker = module_to_match.endswith(ALL_MARKER)

        if starts_with_all_marker and ends_with_al_marker:
            return module_to_match[1:-1] in name

        if starts_with_all_marker:
            return name.endswith(module_to_match[1:])

        if ends_with_al_marker:
            return name.startswith(module_to_match[:-1])

        return module_to_match == name

    @classmethod
    def _convert_to_modules(cls, module_names: Set[str]) -> List[Module]:
        return [Module(name=name) for name in module_names]
