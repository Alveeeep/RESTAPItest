from typing import Optional, List
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from app.dao.base import BaseDAO
from sqlalchemy.future import select
from app.models.activities import Activity
from app.models.secondary import organization_activity


class ActivityDAO(BaseDAO[Activity]):
    model = Activity

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.default_options = [
            selectinload(Activity.children)
            .selectinload(Activity.children)
            .selectinload(Activity.children),
            joinedload(Activity.parent)
        ]

    async def get_tree(self) -> List[Activity]:
        query = (
            select(self.model)
            .options(*self.default_options)
            .filter(self.model.parent_id.is_(None))
            .order_by(self.model.name)
        )
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_with_descendants(
            self,
            activity_id: int
    ) -> Optional[Activity]:
        query = (
            select(self.model)
            .options(*self.default_options)
            .filter(self.model.id == activity_id)
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_level(
            self,
            level: int
    ) -> List[Activity]:
        query = (
            select(self.model)
            .filter(self.model.level == level)
            .order_by(self.model.name)
        )
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_organizations_count(
            self,
            activity_id: int
    ) -> int:
        query = (
            select(func.count(organization_activity.c.organization_id))
            .where(organization_activity.c.activity_id == activity_id)
        )
        return await self._session.scalar(query)

    async def create_activity_tree(
            self,
            name: str,
            parent_id: Optional[int] = None
    ) -> Activity:
        level = 1
        if parent_id:
            parent = await self.find_one_or_none_by_id(parent_id)
            if parent:
                level = parent.level + 1
                if level > 3:
                    raise ValueError("Максимальный уровень вложенности - 3")

        activity = Activity(
            name=name,
            parent_id=parent_id,
            level=level
        )
        self._session.add(activity)
        await self._session.flush()
        return activity
