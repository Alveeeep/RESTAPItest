from pydantic import BaseModel, ConfigDict


class BuildingBase(BaseModel):
    address: str
    latitude: float
    longitude: float


class BuildingCreate(BuildingBase):
    geometry: str
    pass


class BuildingResponse(BuildingBase):
    id: int

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
