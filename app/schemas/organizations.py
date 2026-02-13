from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.schemas.activities import ActivityResponse
from app.schemas.buildings import BuildingResponse
from app.schemas.phones import PhoneResponse


class OrganizationBase(BaseModel):
    name: str
    building_id: int


class OrganizationCreate(OrganizationBase):
    phones: List[str] = Field(default_factory=list)
    activity_ids: List[int] = Field(default_factory=list)


class OrganizationList(OrganizationBase):
    id: int
    building: BuildingResponse
    phones: List[PhoneResponse]
    activities: List[ActivityResponse]

    class Config:
        from_attributes = True


class OrganizationDetail(OrganizationList):
    created_at: datetime
    updated_at: Optional[datetime] = None
