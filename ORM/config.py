import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from passwd.config_DB import ConfigDatabase


class Settings(BaseSettings):
    DB_NAME: str = ConfigDatabase.DBNAME
    DB_USER: str = ConfigDatabase.USER
    DB_PASSWORD: str = ConfigDatabase.PASSWORD
    DB_HOST: str = ConfigDatabase.HOST
    DB_PORT: int = ConfigDatabase.PORT
    model_config = SettingsConfigDict(
        env_file=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '..', '.env'
        )
    )


def get_db_url():
    settings = Settings()

    return (f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASSWORD}"
            f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
