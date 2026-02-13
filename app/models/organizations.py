from typing import List
from app.database.db import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.secondary import organization_activity


class Organization(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False, index=True)

    building_id: Mapped[int] = mapped_column(ForeignKey('buildings.id', ondelete='RESTRICT'))
    building: Mapped['Building'] = relationship(
        'Building',
        back_populates='organizations',
        lazy='joined'
    )

    phones: Mapped[List['Phone']] = relationship(
        'Phone',
        back_populates='organization',
        cascade='all, delete-orphan',
        lazy='selectin'
    )

    activities: Mapped[List['Activity']] = relationship(
        'Activity',
        secondary=organization_activity,
        back_populates='organizations',
        lazy='selectin'
    )
