from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlmodel import SQLModel
from typing import AsyncGenerator 
from app.core.config import get_setting

setting = get_setting()


engine = create_async_engine(
    url=setting.DATABASE_URL, 
    echo=setting.APP_DEBUG, 
    future=True    
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    autoflush=False, 
    autocommit=False, 
    expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]: 
    async with AsyncSessionLocal() as session: 
        try: 
            yield session
            await session.close()
        except: 
            await session.rollback()
            raise


async def init_db():
    async with engine.begin() as conn: 
        await conn.run_sync(SQLModel.metadata.create_all)



