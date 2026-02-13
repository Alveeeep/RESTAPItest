from typing import List

from app.database.db import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry


class Building(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    address: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    geometry: Mapped[Geometry] = mapped_column(
        Geometry('POINT', srid=4326, spatial_index=False),
        nullable=False
    )
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)
    organizations: Mapped[List['Organization']] = relationship(
        'Organization',
        back_populates='building',
        lazy='selectin'
    )
