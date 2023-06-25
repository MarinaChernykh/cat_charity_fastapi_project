from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    """Схема для отображения инфо о пользователях."""
    pass


class UserCreate(schemas.BaseUserCreate):
    """Схема для создания новых пользователей."""
    pass


class UserUpdate(schemas.BaseUserUpdate):
    """Схема для изменения данных о пользователях."""
    pass
