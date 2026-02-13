from typing import List
from app.dao.base import BaseDAO
from sqlalchemy.future import select
from app.models.phones import Phone


class PhoneDAO(BaseDAO[Phone]):
    model = Phone

    async def get_by_organization(
            self,
            organization_id: int
    ) -> List[Phone]:
        query = (
            select(self.model)
            .filter(self.model.organization_id == organization_id)
            .order_by(self.model.number)
        )
        result = await self._session.execute(query)
        return result.scalars().all()
