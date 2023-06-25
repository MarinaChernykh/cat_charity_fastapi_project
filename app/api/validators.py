from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.models import CharityProject


async def check_charity_project_exists(
        charity_project_id: int,
        session: AsyncSession,
) -> CharityProject:
    """Проверяет, существует ли проект с указанным id и возвращает его."""
    charity_project = await charity_project_crud.get(
        charity_project_id, session
    )
    if charity_project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Проект не найден'
        )
    return charity_project


async def check_name_duplicate(
        project_name: str,
        session: AsyncSession,
) -> None:
    """Проверяет, не используется ли уже запрашиваемое название проекта."""
    project_id = await charity_project_crud.get_project_id_by_name(
        project_name, session
    )
    if project_id is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Проект с таким именем уже существует!',
        )


async def check_project_is_open(
    charity_project: CharityProject
) -> None:
    """Проверяет, открыт ли проект."""
    if charity_project.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Закрытый проект нельзя редактировать!',
        )


async def check_project_has_no_donations(
    charity_project: CharityProject
) -> None:
    """Проверяет, были ли сделаны инвестиции в проект."""
    if charity_project.invested_amount > 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='В проект были внесены средства, не подлежит удалению!',
        )


async def check_amount_is_correct(
    charity_project: CharityProject,
    new_amount: int,
) -> None:
    """
    Проверяет, что новый бюджет проекта не меньше,
    чем уже инвестированные в него средства.
    """
    if new_amount < charity_project.invested_amount:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Требуемая сумма не может быть ниже фактически внесенной',
        )
