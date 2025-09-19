'''
These are all global dependencies
'''
from config import engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

# create a sessionmaker bound to async engine
async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# dependency
async def get_session():
    async with async_session_maker() as session:
        yield session
        

        
