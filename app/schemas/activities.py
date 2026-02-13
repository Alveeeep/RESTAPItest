from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class ActivityBase(BaseModel):
    name: str
    level: int


class ActivityCreate(ActivityBase):
    parent_id: int


class ActivitySearchName(BaseModel):
    name: str


class ActivityTree(ActivityBase):
    id: int
    children: List['ActivityTree'] = []

    model_config = ConfigDict(from_attributes=True)


class ActivityResponse(ActivityBase):
    id: int
    parent_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


ActivityTree.model_rebuild()
