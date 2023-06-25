from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, PositiveInt, Field, validator


class CharityProjectCreate(BaseModel):
    """Схема для создания новых проектов."""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    full_amount: PositiveInt

    class Config:
        extra = Extra.forbid


class CharityProjectUpdate(CharityProjectCreate):
    """Схема для внесения изменений в проекты."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1)
    full_amount: Optional[PositiveInt]

    @validator('name')
    def name_cannot_be_null(cls, value: Optional[str]) -> str:
        cls.check_field_is_null('name', value)
        return value

    @validator('description')
    def description_cannot_be_null(cls, value: Optional[str]) -> str:
        cls.check_field_is_null('description', value)
        return value

    @validator('full_amount')
    def amount_cannot_be_null(cls, value: Optional[str]) -> int:
        cls.check_field_is_null('full_amount', value)
        return value

    @staticmethod
    def check_field_is_null(field: str, value: Optional[str]) -> None:
        if value is None:
            raise ValueError(f'Поле {field} не может быть пустым')


class CharityProjectDB(CharityProjectCreate):
    """Схема для отображения инфо о проектах."""
    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime]

    class Config:
        orm_mode = True
