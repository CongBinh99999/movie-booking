from fastapi import Depends 
from app.modules.movies.schemas.domain import GenreCreate, GenreUpdate
from app.shared.dependencies import DbSession
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from uuid import UUID
from app.modules.movies.models import Genres
from sqlalchemy import select, exists
from sqlmodel import col

class GenreRepository: 
    def __init__(self, db: AsyncSession): 
        self.db = db 

    async def get_by_id(self, genre_id: UUID) -> Genres | None: 
        result = await self.db.execute(
            select(Genres)
            .where(Genres.id == genre_id)
        )

        return result.scalar_one_or_none()
    
    async def get_by_slug(self, slug: str)-> Genres | None: 
        result = await self.db.execute(
            select(Genres)
            .where(Genres.slug == slug)
        )

        return result.scalar_one_or_none()
    
    async def get_all(self) -> list[Genres]: 
        result = await self.db.execute(
            select(Genres)
        )

        return list(result.scalars().all())
    
    async def create(self, data:GenreCreate) -> Genres: 
        genre = Genres(**data.model_dump())
        self.db.add(genre)
        await self.db.flush()
        await self.db.refresh(genre)
        return genre
    
    async def update(self, genre:Genres, genre_data:GenreUpdate) -> Genres: 
        data = genre_data.model_dump(exclude_unset=True)

        for key, value in data.items(): 
            setattr(genre, key, value)
        
        await self.db.flush()
        await self.db.refresh(genre)

        return genre

    async def delete(self, genre_id: UUID) -> bool: 
        genre = await self.get_by_id(genre_id=genre_id)

        if genre is None: 
            return False
        
        await self.db.delete(genre)
        await self.db.flush()

        return True 
    
    async def exists_by_name(self, name: str, exclude_id: UUID | None = None) -> bool: 
        subquery = (
            select(1)
            .select_from(Genres)            
            .where(Genres.name == name)
        )

        if exclude_id: 
            subquery = subquery.where(Genres.id != exclude_id)

        result = await self.db.execute(
            select(exists(subquery))      
        )

        return result.scalar_one()
    
    async def exists_by_slug(self, slug: str, exclude_id: UUID | None = None) -> bool: 
        subquery = (
            select(1)
            .select_from(Genres)
            .where(Genres.slug == slug)
        )

        if exclude_id: 
            subquery = subquery.where(Genres.id != exclude_id)

        result = await self.db.execute(
            select(exists(subquery))
        )

        return result.scalar_one() 
    
    async def get_by_ids(self, genre_ids: list[UUID]) -> list[Genres]: 
        if not genre_ids: 
            return []
        
        result = await self.db.execute(
            select(Genres).where(col(Genres.id).in_(genre_ids))
        )

        return list(result.scalars().all())



def get_genre_repository(
    db: DbSession
) -> GenreRepository: 
    return GenreRepository(db)


GenreRepoDep = Annotated[GenreRepository, Depends(get_genre_repository)]