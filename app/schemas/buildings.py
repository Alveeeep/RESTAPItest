from pydantic import BaseModel
from typing import Optional


class BuildingBase(BaseModel):
    address: str
    geometry: str
    latitude: float
    longitude: float


class BuildingCreate(BuildingBase):
    pass


class BuildingResponse(BuildingBase):
    id: int
    organizations_count: Optional[int] = None

    class Config:
        from_attributes = True
