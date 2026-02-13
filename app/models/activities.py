from typing import Optional, List
from app.database.db import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.secondary import organization_activity


class Activity(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False, index=True)
    level: Mapped[int] = mapped_column(default=1, nullable=False)

    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('activities.id', ondelete='CASCADE'),
        nullable=True,
        index=True
    )
    parent: Mapped[Optional['Activity']] = relationship(
        'Activity',
        remote_side=[id],
        back_populates='children',
        lazy='joined'
    )
    children: Mapped[List['Activity']] = relationship(
        'Activity',
        back_populates='parent',
        cascade='all, delete-orphan',
        lazy='selectin'
    )

    organizations: Mapped[List['Organization']] = relationship(
        'Organization',
        secondary=organization_activity,
        back_populates='activities',
        lazy='selectin'
    )
