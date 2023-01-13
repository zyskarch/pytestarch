"""Base class for different graph implementations of an evaluable structure. Delegates direct access to graph nodes
and edges to its subclasses in a template pattern.
"""
from __future__ import annotations

from collections import defaultdict
from itertools import product
from typing import Any, Dict, Iterable, List, Set, Tuple, Union

from pytestarch.eval_structure.breadth_first_searches import (
    any_dependency_to_module_other_than,
    any_other_dependency_to_module_than,
    get_dependency_between_modules,
)
from pytestarch.eval_structure.evaluable_architecture import (
    DependenciesByBaseModules,
    EvaluableArchitecture,
    Module,
    UnexpectedDependenciesByBaseModule,
)
from pytestarch.eval_structure.evaluable_structures import AbstractGraph, AbstractNode
from pytestarch.eval_structure.exceptions import ImpossibleMatch
from pytestarch.eval_structure.utils import get_node

ALL_MARKER = "*"


class EvaluableArchitectureGraph(EvaluableArchitecture):
    """Abstract implementation of an evaluable object that is based on a graph structure."""

    def __init__(self, graph: AbstractGraph) -> None:
        self._graph = graph

    def get_dependencies(
        self,
        dependents: Union[Module, List[Module]],
        dependent_upons: Union[Module, List[Module]],
    ) -> DependenciesByBaseModules:
        result = {}

        dependents = self._listify(dependents)
        dependent_upons = self._listify(dependent_upons)

        dependents, dependent_upons = self._convert_to_full_name_matches(
            [dependents, dependent_upons]
        )

        for dependent, dependent_upon in product(dependents, dependent_upons):
            dependency = get_dependency_between_modules(
                self._graph, dependent, dependent_upon
            )
            result[(dependent, dependent_upon)] = dependency

        return result

    def any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        self,
        dependents: Union[Module, List[Module]],
        dependent_upons: Union[Module, List[Module]],
    ) -> UnexpectedDependenciesByBaseModule:
        result = {}

        dependents = self._listify(dependents)
        dependent_upons = self._listify(dependent_upons)

        dependents, dependent_upons = self._convert_to_full_name_matches(
            [dependents, dependent_upons]
        )

        for dependent in dependents:
            dependencies = any_dependency_to_module_other_than(
                self._graph, dependent, dependent_upons
            )
            result[dependent] = dependencies

        return result

    def _listify(self, module: Union[Module, List[Module]]) -> List[Module]:
        return [module] if not isinstance(module, list) else module

    def any_other_dependencies_on_dependent_upons_than_from_dependents(
        self,
        dependents: Union[Module, List[Module]],
        dependent_upons: Union[Module, List[Module]],
    ) -> UnexpectedDependenciesByBaseModule:
        result = {}

        dependents = self._listify(dependents)
        dependent_upons = self._listify(dependent_upons)

        dependents, dependent_upons = self._convert_to_full_name_matches(
            [dependents, dependent_upons]
        )

        for dependent_upon in dependent_upons:
            dependencies = any_other_dependency_to_module_than(
                self._graph, dependents, dependent_upon
            )
            result[dependent_upon] = dependencies

        return result

    def visualize(self, **kwargs: Any) -> None:
        self._graph.draw(**kwargs)

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
        modules_by_group: Dict[int, List[Any]],
    ) -> Tuple[Dict[int, List[AbstractNode]], Dict[int, List[Module]]]:
        result_by_group: Dict[int, List[Module]] = defaultdict(list)
        partial_match_module_name_by_group: Dict[int, List[AbstractNode]] = {}

        for group, modules in modules_by_group.items():
            partial_match_module_names = []
            result = []

            for node in modules:
                partial_match_module_names.append(
                    get_node(node)
                ) if node.partial_match else result.append(node)

            result_by_group[group] = result
            partial_match_module_name_by_group[group] = partial_match_module_names

        return partial_match_module_name_by_group, result_by_group

    @classmethod
    def _convert_dict_values_to_list_sorted_by_keys(
        cls, d: Dict[Any, Iterable[Any]]
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
