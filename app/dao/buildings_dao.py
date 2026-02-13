from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.dao.base import BaseDAO
from sqlalchemy.future import select
from geoalchemy2 import functions as geo_func
from app.models.buildings import Building
from app.models.organizations import Organization


class BuildingDAO(BaseDAO[Building]):
    model = Building

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.default_options = [
            selectinload(Building.organizations)
            .selectinload(Organization.phones),
            selectinload(Building.organizations)
            .selectinload(Organization.activities)
        ]

    async def get_by_id_with_organizations(
            self,
            building_id: int
    ) -> Optional[Building]:
        query = (
            select(self.model)
            .options(*self.default_options)
            .filter(self.model.id == building_id)
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_nearby(
            self,
            latitude: float,
            longitude: float,
            radius: float,
            limit: int = 100
    ) -> List[Building]:
        point = geo_func.ST_SetSRID(
            geo_func.ST_MakePoint(longitude, latitude),
            4326
        )

        query = (
            select(self.model)
            .where(
                geo_func.ST_DWithin(
                    self.model.geometry,
                    point,
                    radius
                )
            )
            .limit(limit)
        )

        result = await self._session.execute(query)
        return result.scalars().all()
