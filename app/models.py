from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


class Term(SQLModel, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	keyword: str = Field(index=True, unique=True, min_length=1, max_length=128)
	description: str = Field(min_length=1, max_length=2048)
	source: Optional[str] = Field(default=None, max_length=512, description="Источник определения термина")
	
	# Связи, где этот термин является источником
	outgoing_relations: list["TermRelation"] = Relationship(
		back_populates="source_term",
		sa_relationship_kwargs={"cascade_delete": True}
	)
	# Связи, где этот термин является целевым
	incoming_relations: list["TermRelation"] = Relationship(
		back_populates="target_term",
		sa_relationship_kwargs={"cascade_delete": True}
	)


class TermRelation(SQLModel, table=True):
	"""Модель для представления связей между терминами в семантическом графе"""
	id: Optional[int] = Field(default=None, primary_key=True)
	source_id: int = Field(foreign_key="term.id", index=True)
	target_id: int = Field(foreign_key="term.id", index=True)
	relation_type: str = Field(default="related", max_length=64, description="Тип связи (related, synonym, antonym, part_of, etc.)")
	description: Optional[str] = Field(default=None, max_length=512, description="Описание связи")
	
	# Отношения
	source_term: Term = Relationship(back_populates="outgoing_relations")
	target_term: Term = Relationship(back_populates="incoming_relations")
	
	class Config:
		# Уникальность комбинации source_id, target_id, relation_type
		pass