from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):
    database_url: PostgresDsn
    access_token_expires_minutes = 30
    secret_key: str

    auth0_domain: str
    token_algorithm = "RS256"
    token_audience: str
    token_issuer: str
    token_secret: str


settings = Settings()
