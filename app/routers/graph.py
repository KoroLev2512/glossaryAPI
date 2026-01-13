from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..db import get_session
from ..models import Term, TermRelation
from ..schemas import TermRelationCreate, TermRelationRead, GraphData, GraphNode, GraphEdge

router = APIRouter()


@router.post("/relations/", response_model=TermRelationRead, status_code=status.HTTP_201_CREATED)
def create_relation(data: TermRelationCreate, session: Session = Depends(get_session)) -> TermRelation:
	"""Создание связи между терминами"""
	source_term = session.exec(select(Term).where(Term.keyword == data.source_keyword)).first()
	if not source_term:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"Source term '{data.source_keyword}' not found"
		)
	
	target_term = session.exec(select(Term).where(Term.keyword == data.target_keyword)).first()
	if not target_term:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"Target term '{data.target_keyword}' not found"
		)
	
	if source_term.id == target_term.id:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Source and target terms cannot be the same"
		)
	
	# Проверка на существующую связь
	existing = session.exec(
		select(TermRelation).where(
			TermRelation.source_id == source_term.id,
			TermRelation.target_id == target_term.id,
			TermRelation.relation_type == data.relation_type
		)
	).first()
	if existing:
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail="Relation already exists"
		)
	
	relation = TermRelation(
		source_id=source_term.id,
		target_id=target_term.id,
		relation_type=data.relation_type,
		description=data.description
	)
	session.add(relation)
	session.commit()
	session.refresh(relation)
	
	# Загружаем связанные термины для ответа
	session.refresh(relation.source_term)
	session.refresh(relation.target_term)
	
	result = TermRelationRead(
		id=relation.id,
		source_id=relation.source_id,
		target_id=relation.target_id,
		relation_type=relation.relation_type,
		description=relation.description,
		source_keyword=relation.source_term.keyword,
		target_keyword=relation.target_term.keyword
	)
	return result


@router.get("/relations/", response_model=List[TermRelationRead])
def list_relations(session: Session = Depends(get_session)) -> List[TermRelationRead]:
	"""Получение списка всех связей"""
	relations = session.exec(select(TermRelation)).all()
	result = []
	for relation in relations:
		session.refresh(relation.source_term)
		session.refresh(relation.target_term)
		result.append(TermRelationRead(
			id=relation.id,
			source_id=relation.source_id,
			target_id=relation.target_id,
			relation_type=relation.relation_type,
			description=relation.description,
			source_keyword=relation.source_term.keyword,
			target_keyword=relation.target_term.keyword
		))
	return result


@router.get("/relations/{term_keyword}", response_model=List[TermRelationRead])
def get_term_relations(term_keyword: str, session: Session = Depends(get_session)) -> List[TermRelationRead]:
	"""Получение всех связей для конкретного термина"""
	term = session.exec(select(Term).where(Term.keyword == term_keyword)).first()
	if not term:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Term not found")
	
	# Получаем исходящие и входящие связи
	outgoing = session.exec(
		select(TermRelation).where(TermRelation.source_id == term.id)
	).all()
	incoming = session.exec(
		select(TermRelation).where(TermRelation.target_id == term.id)
	).all()
	
	result = []
	for relation in outgoing + incoming:
		session.refresh(relation.source_term)
		session.refresh(relation.target_term)
		result.append(TermRelationRead(
			id=relation.id,
			source_id=relation.source_id,
			target_id=relation.target_id,
			relation_type=relation.relation_type,
			description=relation.description,
			source_keyword=relation.source_term.keyword,
			target_keyword=relation.target_term.keyword
		))
	return result


@router.delete("/relations/{relation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_relation(relation_id: int, session: Session = Depends(get_session)) -> None:
	"""Удаление связи"""
	relation = session.get(TermRelation, relation_id)
	if not relation:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relation not found")
	session.delete(relation)
	session.commit()
	return None


@router.get("/graph", response_model=GraphData)
def get_graph_data(session: Session = Depends(get_session)) -> GraphData:
	"""Получение данных графа для визуализации"""
	# Получаем все термины
	terms = session.exec(select(Term)).all()
	
	# Получаем все связи
	relations = session.exec(select(TermRelation)).all()
	
	# Формируем узлы
	nodes = [
		GraphNode(
			id=term.id,
			keyword=term.keyword,
			description=term.description,
			source=term.source
		)
		for term in terms
	]
	
	# Формируем рёбра
	edges = [
		GraphEdge(
			id=relation.id,
			source=relation.source_id,
			target=relation.target_id,
			relation_type=relation.relation_type,
			description=relation.description
		)
		for relation in relations
	]
	
	return GraphData(nodes=nodes, edges=edges)
