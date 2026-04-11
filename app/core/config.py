from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = ""
    SECRET_KEY: str = ""
    ALGORITHM: str = ""
    ACCESS_TOKEN_EXPIRE: int = 0
    BUCKET_ENDPOINT: str = ""
    BUCKET_ACCESS_KEY: str = ""
    BUCKET_SECRET: str = ""
    BUCKET_NAME: str = ""
    MAIL_HOST: str = ""
    MAIL_PORT: int = 0
    MAIL_SECURE: bool = True
    MAIL_USER: str = ""
    MAIL_PASS: str = ""
    MAIL_FROM: str = "a@a.com"



settings = Settings()
