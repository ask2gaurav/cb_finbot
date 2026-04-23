from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    APP_ENV: str = "development"
    SECRET_KEY: str
    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE: str = ""
    GROQ_API_KEY: str = ""
    LLM_MODEL: str = "llama3-8b-8192"
    EMBEDDING_MODEL: str = "fastembed"
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    MONGODB_URI: str = "mongodb://admin:adminpassword@localhost:27017"
    MONGODB_DB: str = "rag_platform"
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440
    GUARDRAILS_PROVIDER: str = "local"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"]
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

@lru_cache
def get_settings():
    return Settings()
