from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..db import get_session
from ..models import Term
from ..schemas import TermCreate, TermUpdate, TermRead

router = APIRouter()


@router.get("/", response_model=List[TermRead])
def list_terms(session: Session = Depends(get_session)) -> List[Term]:
	return session.exec(select(Term).order_by(Term.keyword)).all()


@router.get("/{keyword}", response_model=TermRead)
def get_term(keyword: str, session: Session = Depends(get_session)) -> Term:
	term = session.exec(select(Term).where(Term.keyword == keyword)).first()
	if not term:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Term not found")
	return term


@router.post("/", response_model=TermRead, status_code=status.HTTP_201_CREATED)
def create_term(data: TermCreate, session: Session = Depends(get_session)) -> Term:
	existing = session.exec(select(Term).where(Term.keyword == data.keyword)).first()
	if existing:
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Term already exists")
	term = Term(keyword=data.keyword, description=data.description)
	session.add(term)
	session.commit()
	session.refresh(term)
	return term


@router.put("/{keyword}", response_model=TermRead)
def update_term(keyword: str, data: TermUpdate, session: Session = Depends(get_session)) -> Term:
	term = session.exec(select(Term).where(Term.keyword == keyword)).first()
	if not term:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Term not found")

	if data.keyword is not None:
		conflict = session.exec(select(Term).where(Term.keyword == data.keyword, Term.id != term.id)).first()
		if conflict:
			raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Keyword already in use")
		term.keyword = data.keyword
	if data.description is not None:
		term.description = data.description

	session.add(term)
	session.commit()
	session.refresh(term)
	return term


@router.delete("/{keyword}", status_code=status.HTTP_204_NO_CONTENT)
def delete_term(keyword: str, session: Session = Depends(get_session)) -> None:
	term = session.exec(select(Term).where(Term.keyword == keyword)).first()
	if not term:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Term not found")
	session.delete(term)
	session.commit()
	return None
