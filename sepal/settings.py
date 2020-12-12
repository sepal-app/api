from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):
    database_url: PostgresDsn
    access_token_expires_minutes = 30
    secret_key: str

    firebase_project_id: str


settings = Settings()
