from typing import Optional

from sqlmodel import SQLModel, Field


class Term(SQLModel, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	keyword: str = Field(index=True, unique=True, min_length=1, max_length=128)
	description: str = Field(min_length=1, max_length=2048)
