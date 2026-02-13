from pydantic import BaseModel


class PhoneBase(BaseModel):
    number: str


class PhoneCreate(PhoneBase):
    organization_id: int


class PhoneResponse(PhoneBase):
    id: int

    class Config:
        from_attributes = True
