from app.database.db import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Phone(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    number: Mapped[str] = mapped_column(nullable=False, index=True)

    organization_id: Mapped[int | None] = mapped_column(ForeignKey('organizations.id', ondelete='CASCADE'))
    organization: Mapped['Organization'] = relationship(
        'Organization',
        back_populates='phones',
        lazy='joined'
    )
