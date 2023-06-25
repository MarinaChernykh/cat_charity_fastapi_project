from typing import Optional, Union, List

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Donation, CharityProject


class CRUDBase:
    """Базовые CRUD операции для работы с БД."""

    def __init__(self, model):
        self.model = model

    async def get(
            self,
            obj_id: int,
            session: AsyncSession,
    ):
        """Возвращает объект по его id."""
        db_obj = await session.execute(
            select(self.model).where(
                self.model.id == obj_id
            )
        )
        return db_obj.scalars().first()

    async def get_multi(
            self,
            session: AsyncSession
    ):
        """Возвращает список всех объектов модели."""
        db_objs = await session.execute(select(self.model))
        return db_objs.scalars().all()

    async def get_open_objects(
            self,
            session: AsyncSession,
    ) -> Union[List[Donation], List[CharityProject]]:
        """Возвращает список открытых пожертвований / проектов."""
        open_objects = await session.execute(
            select(self.model).where(
                self.model.fully_invested == 0
            )
        )
        return open_objects.scalars().all()

    async def create_db_object(
            self,
            obj_in,
            user: Optional[User] = None
    ):
        """
        Создает новый объект модели и возвращает его,
        НЕ ЗАПИСЫВАЯ В БАЗУ,
        для расчета и внесения инвестиций.
        """
        obj_in_data = obj_in.dict()
        if user is not None:
            obj_in_data['user_id'] = user.id
        db_obj = self.model(**obj_in_data)
        return db_obj

    async def commit_creation(
            self,
            db_obj,
            objects_to_be_comitted,
            session: AsyncSession,
    ):
        """
        Записывает в базу новый объект, а также проекты / пожертвования,
        суммы по которым / статусы были изменены при распределении инвестиций,
        вызванных созданием нового объекта.
        """
        session.add(db_obj)
        for obj in objects_to_be_comitted:
            session.add(obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
            self,
            db_obj,
            obj_in,
            session: AsyncSession,
    ):
        """Вносит изменения в объект базы данных."""
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def remove(
            self,
            db_obj,
            session: AsyncSession,
    ):
        """Удаляет объект из базы данных."""
        await session.delete(db_obj)
        await session.commit()
        return db_obj
