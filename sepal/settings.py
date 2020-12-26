from typing import Optional
from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):
    app_base_url: str
    database_url: PostgresDsn

    firebase_project_id: str
    google_application_credentials_json: Optional[str] = None

    mailgun_api_key: str
    mailgun_api_url: str


settings = Settings()
