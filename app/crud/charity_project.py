from typing import Optional, List, Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject


class CRUDCharityProject(CRUDBase):
    """Дополнительные CRUD методы для работы с проектами."""

    async def get_project_id_by_name(
            self,
            project_name: str,
            session: AsyncSession,
    ) -> Optional[int]:
        """Возвращает id объекта с указанным именем."""
        db_project_id = await session.execute(
            select(CharityProject.id).where(
                CharityProject.name == project_name
            )
        )
        db_project_id = db_project_id.scalars().first()
        return db_project_id

    async def get_projects_by_completion_rate(
        self,
        session: AsyncSession,
    ) -> List[Dict[str, str]]:
        """
        Возвращает список данных о закрытых проектах,
        отсортированный по возрастанию периода
        от открытия до закрытия.
        """
        closed_objects = await session.execute(
            select(CharityProject).where(
                CharityProject.fully_invested == 1
            )
        )
        return sorted(
            [
                {'name': obj.name,
                 'period': str(obj.close_date - obj.create_date),
                 'description': obj.description}
                for obj in closed_objects.scalars().all()
            ],
            key=lambda obj: obj['period']
        )


charity_project_crud = CRUDCharityProject(CharityProject)
