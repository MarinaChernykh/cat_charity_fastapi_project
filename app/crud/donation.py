from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Donation, User


class CRUDDonation(CRUDBase):
    """Дополнительные CRUD методы для работы с пожертвованиями."""

    async def get_by_user(
        self,
        session: AsyncSession,
        user: User,
    ) -> List[Donation]:
        """Возвращает список пожертвований пользователя."""
        donations = await session.execute(
            select(Donation).where(
                Donation.user_id == user.id
            )
        )
        return donations.scalars().all()


donation_crud = CRUDDonation(Donation)
