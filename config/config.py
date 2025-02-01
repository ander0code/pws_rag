import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Optional

env = os.getenv("ENV", "development")
env_file = f".env.{env}" if env != "production" else ".env"

print(f"Cargando configuración desde: {env_file}")  

load_dotenv(env_file)

class AppEnv(BaseSettings):

    QDRANT_URL : str
    APP_PORT: Optional[int] = 8000
    REDIS_URL: str
    REDIS_SESSION_TTL: int
    OPENAI_API_KEY: str

    class Config:
        env_file = env_file
        env_file_encoding = "utf-8"

app_env = AppEnv()
    
