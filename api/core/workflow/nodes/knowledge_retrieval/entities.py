from typing import Any, Literal, Optional

from pydantic import BaseModel

from core.workflow.entities.base_node_data_entities import BaseNodeData


class RerankingModelConfig(BaseModel):
    """
    Reranking Model Config.
    """
    provider: str
    model: str


class VectorSetting(BaseModel):
    """
    Vector Setting.
    """
    vector_weight: float
    embedding_provider_name: str
    embedding_model_name: str


class KeywordSetting(BaseModel):
    """
    Keyword Setting.
    """
    keyword_weight: float


class WeightedScoreConfig(BaseModel):
    """
    Weighted score Config.
    """
    weight_type: str
    vector_setting: VectorSetting
    keyword_setting: KeywordSetting


class MultipleRetrievalConfig(BaseModel):
    """
    Multiple Retrieval Config.
    """
    top_k: int
    score_threshold: Optional[float] = None
    reranking_mode: str = 'reranking_model'
    reranking_enable: bool = False
    reranking_model: RerankingModelConfig
    weights: WeightedScoreConfig


class ModelConfig(BaseModel):
    """
     Model Config.
    """
    provider: str
    name: str
    mode: str
    completion_params: dict[str, Any] = {}


class SingleRetrievalConfig(BaseModel):
    """
    Single Retrieval Config.
    """
    model: ModelConfig


class KnowledgeRetrievalNodeData(BaseNodeData):
    """
    Knowledge retrieval Node Data.
    """
    type: str = 'knowledge-retrieval'
    query_variable_selector: list[str]
    dataset_ids: list[str]
    retrieval_mode: Literal['single', 'multiple']
    multiple_retrieval_config: Optional[MultipleRetrievalConfig] = None
    single_retrieval_config: Optional[SingleRetrievalConfig] = None
