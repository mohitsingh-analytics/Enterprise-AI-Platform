from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    anthropic_api_key: str
    model_name: str
    temperature: float
    max_tokens: int
    model_provider: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()