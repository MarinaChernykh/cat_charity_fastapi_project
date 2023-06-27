from datetime import datetime
from typing import List, Dict

from aiogoogle import Aiogoogle

from app.core.config import settings


FORMAT = "%Y/%m/%d %H:%M:%S"
ROW_COUNT = 100
COLUMN_COUNT = 11
RANGE = 'A1:E30'


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    """Создает google-документ(spreadsheet)."""
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    spreadsheet_body = {
        'properties': {'title': f'Отчет от {now_date_time}',
                       'locale': 'ru_RU'},
        'sheets': [
            {
                'properties': {'sheetType': 'GRID',
                               'sheetId': 0,
                               'title': 'Лист1',
                               'gridProperties': {'rowCount': ROW_COUNT,
                                                  'columnCount': COLUMN_COUNT}}
            }
        ]
    }
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    spreadsheet_id = response['spreadsheetId']
    return spreadsheet_id


async def set_user_permissions(
        spreadsheet_id: str,
        wrapper_services: Aiogoogle
) -> None:
    """Предоставляет права доступа к google-документу."""
    permissions_body = {'type': 'user',
                        'role': 'writer',
                        'emailAddress': settings.email}
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,
            json=permissions_body,
            fields="id"
        ))


async def spreadsheets_update_value(
        spreadsheet_id: str,
        projects: List[Dict[str, str]],
        wrapper_services: Aiogoogle
) -> None:
    """Вносит данные в google-документ."""
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    table_values = [
        ['Отчет от', now_date_time],
        ['Топ проектов по скорости закрытия'],
        ['Название проекта', 'Время сбора', 'Описание']
    ]
    table_values.extend(
        [
            [project['name'], project['period'], project['description']]
            for project in projects
        ]
    )

    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values
    }
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=RANGE,
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )
