from dotenv import load_dotenv, find_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = find_dotenv()
load_dotenv(env_path)


class DatabaseConfig(BaseSettings):
    dsn: str = Field("", alias="DSN")
    image_path: str


class TgBot(BaseSettings):
    token: str = Field(..., alias="bot_token")
    yukassa_token: str = Field(..., alias="YUKASSA_TOKEN")
    required_channel: str


class ConfigSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    tg_bot: TgBot = TgBot()
    db: DatabaseConfig = DatabaseConfig()
    env_type: str = Field("test", env="ENV_TYPE")
    report_path: str


config_settings = ConfigSettings()
