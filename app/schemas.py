from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class TermCreate(BaseModel):
	keyword: str = Field(min_length=1, max_length=128)
	description: str = Field(min_length=1, max_length=2048)
	source: Optional[str] = Field(default=None, max_length=512, description="Источник определения термина")


class TermUpdate(BaseModel):
	keyword: Optional[str] = Field(default=None, min_length=1, max_length=128)
	description: Optional[str] = Field(default=None, min_length=1, max_length=2048)
	source: Optional[str] = Field(default=None, max_length=512, description="Источник определения термина")


class TermRead(BaseModel):
	model_config = ConfigDict(from_attributes=True)
	id: int
	keyword: str
	description: str
	source: Optional[str] = None


class TermRelationCreate(BaseModel):
	source_keyword: str = Field(min_length=1, max_length=128, description="Ключевое слово термина-источника")
	target_keyword: str = Field(min_length=1, max_length=128, description="Ключевое слово термина-цели")
	relation_type: str = Field(default="related", max_length=64, description="Тип связи (related, synonym, antonym, part_of, etc.)")
	description: Optional[str] = Field(default=None, max_length=512, description="Описание связи")


class TermRelationRead(BaseModel):
	model_config = ConfigDict(from_attributes=True)
	id: int
	source_id: int
	target_id: int
	relation_type: str
	description: Optional[str] = None
	source_keyword: str
	target_keyword: str


class GraphNode(BaseModel):
	"""Узел графа для визуализации"""
	id: int
	keyword: str
	description: str
	source: Optional[str] = None


class GraphEdge(BaseModel):
	"""Ребро графа для визуализации"""
	id: int
	source: int  # ID узла-источника
	target: int  # ID узла-цели
	relation_type: str
	description: Optional[str] = None


class GraphData(BaseModel):
	"""Данные графа для фронтенда"""
	nodes: list[GraphNode]
	edges: list[GraphEdge]