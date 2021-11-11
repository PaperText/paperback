from abc import ABCMeta, abstractmethod
from typing import List, TypedDict

from py2neo import Node, Relationship

CypherQuery = str


class AnalyzerResult(TypedDict):
    nodes: List[Node]
    relationships: List[Relationship]
    commands_to_run: List[CypherQuery]


class Analyzer(metaclass=ABCMeta):
    @abstractmethod
    def process(self, text: str, parent_node: Node) -> AnalyzerResult:
        """Process text and connect to `parent_node`

        Parameters
        ----------
        text: str
            text to analyze
        parent_node: Node
            parent node to attach relations

        Returns
        -------
        AnalyzerResult
            nodes and relationships to create
        """
        raise NotImplemented("method `process` must be implemented")

    def __call__(self, text: str, parent_node: Node) -> AnalyzerResult:
        """shortcut to process"""
        return self.process(text, parent_node)
