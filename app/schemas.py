from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class TermCreate(BaseModel):
	keyword: str = Field(min_length=1, max_length=128)
	description: str = Field(min_length=1, max_length=2048)


class TermUpdate(BaseModel):
	keyword: Optional[str] = Field(default=None, min_length=1, max_length=128)
	description: Optional[str] = Field(default=None, min_length=1, max_length=2048)


class TermRead(BaseModel):
	model_config = ConfigDict(from_attributes=True)
	id: int
	keyword: str
	description: str
