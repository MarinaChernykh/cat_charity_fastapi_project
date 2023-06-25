from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.schemas.charity_project import (
    CharityProjectDB, CharityProjectCreate, CharityProjectUpdate)
from app.services.investments import make_investments
from app.api.validators import (
    check_charity_project_exists, check_name_duplicate, check_project_is_open,
    check_amount_is_correct, check_project_has_no_donations)


router = APIRouter()


@router.get(
    '/',
    response_model=list[CharityProjectDB],
    response_model_exclude_none=True,
)
async def get_all_charity_projects(
    session: AsyncSession = Depends(get_async_session),
):
    """
    Для всех пользователей.
    Возвращает список всех проектов.
    """
    all_projects = await charity_project_crud.get_multi(session)
    return all_projects


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_new_charity_project(
    charity_project: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Только для суперюзеров.
    Создает новый проект и вносит в него пожертвования,
    если есть нераспределенные деньги.
    """
    await check_name_duplicate(charity_project.name, session)
    new_project = await charity_project_crud.create_db_object(
        charity_project
    )
    new_project, donations_updated = await make_investments(
        new_project, session
    )
    new_project = await charity_project_crud.commit_creation(
        new_project, donations_updated, session
    )
    return new_project


@router.patch(
    '/{charity_project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def partially_update_charity_project(
        charity_project_id: int,
        obj_in: CharityProjectUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    """
    Только для суперюзеров.
    Вносит изменения в разрешенные поля существующего проекта.
    """
    charity_project = await check_charity_project_exists(
        charity_project_id, session
    )
    await check_project_is_open(charity_project)
    if obj_in.name is not None:
        await check_name_duplicate(obj_in.name, session)
    if obj_in.full_amount is not None:
        await check_amount_is_correct(charity_project, obj_in.full_amount)
        if obj_in.full_amount == charity_project.invested_amount:
            charity_project.fully_invested = True
            charity_project.close_date = datetime.utcnow()

    charity_project = await charity_project_crud.update(
        charity_project, obj_in, session
    )
    return charity_project


@router.delete(
    '/{charity_project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def remove_charity_project(
        charity_project_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """
    Только для суперюзеров.
    Удаляет проект, при условии что на него не были выделены инвестиции.
    """
    charity_project = await check_charity_project_exists(
        charity_project_id, session
    )
    await check_project_has_no_donations(charity_project)
    charity_project = await charity_project_crud.remove(
        charity_project, session
    )
    return charity_project
