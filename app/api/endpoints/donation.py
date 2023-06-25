from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_user, current_superuser
from app.crud.donation import donation_crud
from app.models import User
from app.schemas.donation import DonationDB, DonationCreate
from app.services.investments import make_investments


router = APIRouter()


@router.post(
    '/',
    response_model=DonationDB,
    response_model_exclude_none=True,
    response_model_exclude={
        'user_id', 'invested_amount', 'fully_invested', 'close_date'
    },
)
async def create_donation(
    donation: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """
    Для авторизованных пользователей.
    Создает новое пожертвование и инвестирует его в проекты,
    если есть открытые.
    """
    new_donation = await donation_crud.create_db_object(
        donation, user
    )
    new_donation, projects_updated = await make_investments(
        new_donation, session
    )
    new_donation = await donation_crud.commit_creation(
        new_donation, projects_updated, session
    )
    return new_donation


@router.get(
    '/',
    response_model=list[DonationDB],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session),
):
    """
    Только для суперюзеров.
    Возвращает список всех пожертвований.
    """
    all_donations = await donation_crud.get_multi(session)
    return all_donations


@router.get(
    '/my',
    response_model=list[DonationDB],
    response_model_exclude={
        'user_id', 'invested_amount', 'fully_invested', 'close_date'
    },
)
async def get_my_donations(
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Для авторизованных пользователей.
    Возвращает список пожертвований текущего пользователя.
    """
    donations = await donation_crud.get_by_user(session, user)
    return donations
