from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    openrouter_api_key: str
    redis_url: str
    default_model: str
    default_ttl_hours:int
    model_config = SettingsConfigDict(env_file='.env')
settings = Settings()