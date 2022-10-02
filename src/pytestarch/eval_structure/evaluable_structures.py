from abc import ABC, abstractmethod
from typing import List

AbstractNode = str


class AbstractGraph(ABC):
    @abstractmethod
    def direct_successor_nodes(self, node: AbstractNode) -> List[AbstractNode]:
        raise NotImplementedError()

    @abstractmethod
    def parent_child_relationship(
        self, parent: AbstractNode, child: AbstractNode
    ) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def direct_predecessor_nodes(self, node: AbstractNode) -> List[AbstractNode]:
        raise NotImplementedError()
