from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./youtube_shorts.db"
    STATIC_FILES_DIR: str = "static"
    TEMPLATES_DIR: str = str(Path(__file__).parent / "templates")
    
    class Config:
        env_file = ".env"

settings = Settings() 