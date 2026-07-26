from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    anthropic_api_key: str
    model_name: str
    temperature: float
    max_tokens: int
    model_provider: str
    
    class Config:
        env_file=".env"     


settings= Settings()
