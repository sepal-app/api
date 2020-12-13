from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):
    app_base_url: str
    database_url: PostgresDsn
    access_token_expires_minutes = 30
    secret_key: str

    firebase_project_id: str

    mailgun_api_key: str
    mailgun_api_url: str


settings = Settings()
