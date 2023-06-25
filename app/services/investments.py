from datetime import datetime
from typing import List, Union

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation
from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud


async def check_if_ready_and_close(
    obj: Union[CharityProject, Donation]
) -> Union[CharityProject, Donation]:
    """Закрывает проект / пожертвование, если сумма набрана."""
    if obj.full_amount == obj.invested_amount:
        obj.fully_invested = True
        obj.close_date = datetime.utcnow()
    return obj


async def get_uninvested_amount(
    obj: Union[CharityProject, Donation]
) -> int:
    """
    Расчитывает сумму, необходимую для закрытия проекта
    или непотраченную сумму из пожертвования.
    """
    if obj.invested_amount is None:
        obj.invested_amount = 0
    return obj.full_amount - obj.invested_amount


async def make_investments(
    new_obj: Union[CharityProject, Donation],
    session: AsyncSession,
) -> List[Union[CharityProject, Donation]]:
    """
    Распределяет инвестиции по проектам и вносит
    соответствующие изменения в проекты и пожертвования
    (статус (открыт / закрыт), дата закрытия,
    фактическая сумма инвестиций).
    """
    objects_to_be_comitted = []

    if isinstance(new_obj, CharityProject):
        open_investments = await donation_crud.get_open_objects(session)
    elif isinstance(new_obj, Donation):
        open_investments = await charity_project_crud.get_open_objects(
            session
        )

    while not new_obj.fully_invested and open_investments:
        open_investments_obj = open_investments.pop(0)
        amount_to_invest = min(
            await get_uninvested_amount(new_obj),
            await get_uninvested_amount(open_investments_obj)
        )

        new_obj.invested_amount += amount_to_invest
        new_obj = await check_if_ready_and_close(new_obj)

        open_investments_obj.invested_amount += amount_to_invest
        open_investments_obj = await check_if_ready_and_close(
            open_investments_obj
        )
        objects_to_be_comitted.append(open_investments_obj)

    return new_obj, objects_to_be_comitted
