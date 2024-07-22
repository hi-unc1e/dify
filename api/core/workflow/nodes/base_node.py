from abc import ABC, abstractmethod
from collections.abc import Generator, Mapping
from typing import Any, Optional

from core.workflow.entities.base_node_data_entities import BaseIterationState, BaseNodeData
from core.workflow.entities.node_entities import NodeRunResult, NodeType
from core.workflow.entities.variable_pool import VariablePool
from core.workflow.graph_engine.entities.graph import Graph
from core.workflow.graph_engine.entities.graph_init_params import GraphInitParams
from core.workflow.graph_engine.entities.graph_runtime_state import GraphRuntimeState
from core.workflow.nodes.event import RunCompletedEvent, RunEvent
from core.workflow.nodes.iterable_node_mixin import IterableNodeMixin


class BaseNode(ABC):
    _node_data_cls: type[BaseNodeData]
    _node_type: NodeType

    def __init__(self,
                 config: Mapping[str, Any],
                 graph_init_params: GraphInitParams,
                 graph: Graph,
                 graph_runtime_state: GraphRuntimeState,
                 previous_node_id: Optional[str] = None) -> None:
        self.tenant_id = graph_init_params.tenant_id
        self.app_id = graph_init_params.app_id
        self.workflow_type = graph_init_params.workflow_type
        self.workflow_id = graph_init_params.workflow_id
        self.user_id = graph_init_params.user_id
        self.user_from = graph_init_params.user_from
        self.invoke_from = graph_init_params.invoke_from
        self.workflow_call_depth = graph_init_params.call_depth
        self.graph = graph
        self.graph_runtime_state = graph_runtime_state
        self.previous_node_id = previous_node_id

        node_id = config.get("id")
        if not node_id:
            raise ValueError("Node ID is required.")

        self.node_id = node_id
        self.node_data = self._node_data_cls(**config.get("data", {}))

    @abstractmethod
    def _run(self) \
            -> NodeRunResult | Generator[RunEvent, None, None]:
        """
        Run node
        :return:
        """
        raise NotImplementedError

    def run(self) -> Generator[RunEvent, None, None]:
        """
        Run node entry
        :return:
        """
        result = self._run()

        if isinstance(result, NodeRunResult):
            yield RunCompletedEvent(
                run_result=result
            )
        else:
            yield from result

    @classmethod
    def extract_variable_selector_to_variable_mapping(cls, config: dict) -> dict[str, list[str]]:
        """
        Extract variable selector to variable mapping
        :param config: node config
        :return:
        """
        node_data = cls._node_data_cls(**config.get("data", {}))
        return cls._extract_variable_selector_to_variable_mapping(node_data)

    @classmethod
    @abstractmethod
    def _extract_variable_selector_to_variable_mapping(cls, node_data: BaseNodeData) -> dict[str, list[str]]:
        """
        Extract variable selector to variable mapping
        :param node_data: node data
        :return:
        """
        raise NotImplementedError

    @classmethod
    def get_default_config(cls, filters: Optional[dict] = None) -> dict:
        """
        Get default config of node.
        :param filters: filter by node config parameters.
        :return:
        """
        return {}

    @property
    def node_type(self) -> NodeType:
        """
        Get node type
        :return:
        """
        return self._node_type


class BaseIterationNode(BaseNode, IterableNodeMixin):
    @abstractmethod
    def _run(self) -> BaseIterationState:
        """
        Run node
        :return:
        """
        raise NotImplementedError

    def run(self) -> BaseIterationState:
        """
        Run node entry
        :return:
        """
        return self._run(variable_pool=self.graph_runtime_state.variable_pool)

    def get_next_iteration(self, variable_pool: VariablePool, state: BaseIterationState) -> NodeRunResult | str:
        """
        Get next iteration start node id based on the graph.
        :param graph: graph
        :return: next node id
        """
        return self._get_next_iteration(variable_pool, state)

    @abstractmethod
    def _get_next_iteration(self, variable_pool: VariablePool, state: BaseIterationState) -> NodeRunResult | str:
        """
        Get next iteration start node id based on the graph.
        :param graph: graph
        :return: next node id
        """
        raise NotImplementedError
