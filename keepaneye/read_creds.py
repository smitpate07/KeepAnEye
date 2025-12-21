from pydantic_settings import BaseSettings, SettingsConfigDict

class AppConfig(BaseSettings):
    API_KEY: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

# Load configuration from environment
#config = AppConfig()

