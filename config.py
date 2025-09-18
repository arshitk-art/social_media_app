from pydantic import  AnyHttpUrl
from pydantic_settings import BaseSettings
from typing import List
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from fastapi import FastAPI
from sqlmodel import SQLModel,create_engine
from sqlalchemy.ext.asyncio import AsyncEngine



class Settings(BaseSettings):
    APP_NAME: str = "Social Media API"
    DEBUG: bool = True
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 300
    ALLOWED_ORIGINS: List[AnyHttpUrl] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = True
        
    @property
    def get_database_url(self):
        return self.DATABASE_URL

settings = Settings()

engine = create_async_engine(
    settings.DATABASE_URL,  # must be asyncpg URL
    echo=True,
)

# async def initdb():
#     """create our database models in the database"""

#     async with engine.begin() as conn:
#         await conn.run_sync(SQLModel.metadata.create_all)



