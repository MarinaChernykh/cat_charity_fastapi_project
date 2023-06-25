from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    app_title: str = 'QR_Kot'
    app_description: str = 'Добрый сервис для помощи котикам'
    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'
    secret_key: str = 'SECRET'
    type: Optional[str] = None
    project_id: Optional[str] = None
    private_key_id: Optional[str] = None
    private_key: Optional[str] = None
    client_email: Optional[str] = None
    client_id: Optional[str] = None
    auth_uri: Optional[str] = None
    token_uri: Optional[str] = None
    auth_provider_x509_cert_url: Optional[str] = None
    client_x509_cert_url: Optional[str] = None
    email: Optional[str] = None

    class Config:
        env_file = '.env'


settings = Settings()
