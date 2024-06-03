from __future__ import annotations

from abc import ABC, abstractmethod

AbstractNode = str


class AbstractGraph(ABC):
    @abstractmethod
    def direct_successor_nodes(self, node: AbstractNode) -> list[AbstractNode]:
        raise NotImplementedError()

    @abstractmethod
    def parent_child_relationship(
        self, parent: AbstractNode, child: AbstractNode
    ) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def direct_predecessor_nodes(self, node: AbstractNode) -> list[AbstractNode]:
        raise NotImplementedError()

    @property
    @abstractmethod
    def nodes(self) -> list[AbstractNode]:
        raise NotImplementedError()
