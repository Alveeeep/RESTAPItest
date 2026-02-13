from sqlalchemy import Table, Column, ForeignKey
from app.database.db import Base

organization_activity = Table(
    'organization_activity',
    Base.metadata,
    Column('organization_id', ForeignKey('organizations.id', ondelete='CASCADE'), primary_key=True),
    Column('activity_id', ForeignKey('activities.id', ondelete='CASCADE'), primary_key=True)
)
