from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from app.dao.activities_dao import ActivityDAO
from app.dao.base import BaseDAO
from sqlalchemy.future import select
from loguru import logger
from geoalchemy2 import functions as geo_func
from app.models.activities import Activity
from app.models.buildings import Building
from app.models.phones import Phone
from app.schemas.organizations import OrganizationCreate
from app.models.organizations import Organization


class OrganizationDAO(BaseDAO[Organization]):
    model = Organization

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.default_options = [
            selectinload(Organization.phones),
            selectinload(Organization.activities),
            joinedload(Organization.building)
        ]
        self.activity_dao = ActivityDAO(session)

    async def get_by_id_with_relations(self, org_id: int) -> Optional[Organization]:
        logger.info(f"Получение организации с ID {org_id} со всеми связями")
        query = (
            select(self.model)
            .options(*self.default_options)
            .filter(self.model.id == org_id)
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_building(
            self,
            building_id: int
    ) -> List[Organization]:
        logger.info(f"Получение организаций в здании {building_id}")
        query = (
            select(self.model)
            .options(*self.default_options)
            .filter(self.model.building_id == building_id)
        )
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_by_activity_direct(
            self,
            activity_id: int
    ) -> List[Organization]:
        logger.info(f"Получение организаций по деятельности {activity_id}")
        query = (
            select(self.model)
            .options(*self.default_options)
            .join(Organization.activities)
            .filter(Activity.id == activity_id)
        )
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_by_activity_with_children(
            self,
            activity_id: int
    ) -> List[Organization]:
        logger.info(f"Получение организаций по деятельности {activity_id} с подкатегориями")

        cte = (
            select(Activity.id)
            .where(Activity.id == activity_id)
            .cte(name="activity_tree", recursive=True)
        )

        cte = cte.union_all(
            select(Activity.id)
            .where(Activity.parent_id == cte.c.id)
        )

        query = (
            select(self.model)
            .options(*self.default_options)
            .distinct()
            .join(Organization.activities)
            .join(cte, Activity.id == cte.c.id)
        )

        result = await self._session.execute(query)
        return result.scalars().all()

    async def search_by_name(
            self,
            query: str
    ) -> List[Organization]:
        logger.info(f"Поиск организаций по названию: {query}")
        search_query = (
            select(self.model)
            .options(*self.default_options)
            .filter(self.model.name.ilike(f"%{query}%"))
        )
        result = await self._session.execute(search_query)
        return result.scalars().all()

    async def get_nearby_radius(
            self,
            latitude: float,
            longitude: float,
            radius: float
    ) -> List[Organization]:
        logger.info(f"Поиск организаций в радиусе {radius}м от ({latitude}, {longitude})")

        point = geo_func.ST_SetSRID(
            geo_func.ST_MakePoint(longitude, latitude),
            4326
        )

        query = (
            select(self.model)
            .options(*self.default_options)
            .join(self.model.building)
            .where(
                geo_func.ST_DWithin(
                    Building.geometry,
                    point,
                    radius
                )
            )
        )

        result = await self._session.execute(query)
        return result.scalars().all()

    async def create_organization(
            self,
            org_data: OrganizationCreate
    ) -> Organization:
        logger.info(f"Создание организации: {org_data.name}")

        organization = Organization(
            name=org_data.name,
            building_id=org_data.building_id,
            phones=[Phone(number=phone) for phone in org_data.phones]
        )

        if org_data.activity_ids:
            activities = []
            for activity_id in org_data.activity_ids:
                activity = await self.activity_dao.find_one_or_none_by_id(activity_id)
                if activity:
                    activities.append(activity)
            if activities:
                organization.activities = activities

        self._session.add(organization)
        await self._session.commit()
        logger.info(f"Создана организация ID={organization.id}, телефонов: {len(organization.phones)}")
        for phone in organization.phones:
            logger.info(f"Телефон: {phone.number}, org_id={phone.organization_id}")
        return await self.get_by_id_with_relations(organization.id)
