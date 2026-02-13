from pydantic import BaseModel
from typing import Optional
from geoalchemy2 import Geometry


class BuildingBase(BaseModel):
    address: str
    geometry: Geometry
    latitude: float
    longitude: float


class BuildingCreate(BuildingBase):
    pass


class BuildingResponse(BuildingBase):
    id: int
    organizations_count: Optional[int] = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
