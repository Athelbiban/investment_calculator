import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from passwd.config_DB import DBNAME, USER, PASSWORD, HOST, PORT


class Settings(BaseSettings):
    DB_NAME: str = DBNAME
    DB_USER: str = USER
    DB_PASSWORD: str = PASSWORD
    DB_HOST: str = HOST
    DB_PORT: int = PORT
    model_config = SettingsConfigDict(
        env_file=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '..', '.env'
        )
    )


def get_db_url() -> str:
    settings = Settings()

    return (f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASSWORD}"
            f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
