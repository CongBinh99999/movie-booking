from fastapi import Depends 
from app.modules.movies.repository.genre_repository import GenreRepoDep, GenreRepository
from app.modules.movies.repository.movie_repository import MovieRepoDep, MovieRepository
from app.modules.movies.repository.movie_genre_repository import MovieGenreRepoDep, MovieGenreRepository
from typing import Annotated
from uuid import UUID
from app.modules.movies.schemas.domain import GenreDTO, GenreCreate, GenreUpdate, MovieDTO
from app.modules.movies.exceptions.genre_exception import (
    GenreNotFoundError,
    GenreAlreadyExistsError,
    GenreHasMoviesError,
)
import re
import unicodedata

class GenreService: 
    def __init__(
        self,
        genre_repo: GenreRepository,
        movie_genre_repo: MovieGenreRepository,
        movie_repo: MovieRepository
    ): 
        self.genre_repo = genre_repo
        self.movie_genre_repo = movie_genre_repo
        self.movie_repo = movie_repo


    async def get_genre(self, genre_id: UUID) -> GenreDTO: 
        genre = await self.genre_repo.get_by_id(genre_id)

        if genre is None:
            raise GenreNotFoundError(genre_id)

        return GenreDTO.model_validate(genre)
    

    async def get_genres(self) -> list[GenreDTO]: 
        genres = await self.genre_repo.get_all()

        return list(GenreDTO.model_validate(genre) for genre in genres)
    
    
    async def create_genre(self, data: GenreCreate) -> GenreDTO:
        name = data.name
        slug = data.slug or self._generate_slug(name)

        if await self.genre_repo.exists_by_name(name):
            raise GenreAlreadyExistsError(name)
        
        if await self.genre_repo.exists_by_slug(slug):
            raise GenreAlreadyExistsError(slug)

        payload = data.model_copy(update={"slug": slug})
        genre = await self.genre_repo.create(payload)

        return GenreDTO.model_validate(genre)


    async def update_genre(self, genre_id: UUID, data: GenreUpdate) -> GenreDTO: 
        genre = await self.genre_repo.get_by_id(genre_id)

        if genre is None: 
            raise GenreNotFoundError(genre_id)
        
        name = data.name 
        slug = data.slug
        if name and not slug:
            slug = self._generate_slug(name)

        if name and name != genre.name: 
            if await self.genre_repo.exists_by_name(name, exclude_id=genre_id):
                raise GenreAlreadyExistsError(name)
            
        if slug and slug != genre.slug: 
            if await self.genre_repo.exists_by_slug(slug, exclude_id=genre_id): 
                raise GenreAlreadyExistsError(slug)

        if slug and slug != data.slug:
            data = data.model_copy(update={"slug": slug})
            
        updated = await self.genre_repo.update(genre=genre, genre_data=data)

        return GenreDTO.model_validate(updated)
        

    
    async def delete_genre(self, genre_id: UUID) -> None: 
        genre = await self.genre_repo.get_by_id(genre_id)

        if genre is None: 
            raise GenreNotFoundError(genre_id)
        
        movie_ids = await self.movie_genre_repo.get_movie_ids_for_genre(genre_id)
        if movie_ids:
            raise GenreHasMoviesError(genre_id, len(movie_ids))

        await self.genre_repo.delete(genre_id=genre_id)


    async def get_movies_for_genre(
        self,
        genre_id: UUID,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[list[MovieDTO], int]:
        genre = await self.genre_repo.get_by_id(genre_id)
        if genre is None:
            raise GenreNotFoundError(genre_id)

        movie_ids = await self.movie_genre_repo.get_movie_ids_for_genre(genre_id)
        total = len(movie_ids)

        movies = await self.movie_repo.get_by_genre(
            genre_id=genre_id,
            skip=skip,
            limit=limit
        )

        return [MovieDTO.model_validate(m) for m in movies], total
    

    def _generate_slug(self, name: str) -> str: 
        if not name:
            return ""

        slug = name.strip().lower()

        slug = unicodedata.normalize("NFD", slug)
        slug = "".join(ch for ch in slug if unicodedata.category(ch) != "Mn")

        slug = slug.replace("đ", "d")

        slug = re.sub(r"[^a-z0-9]+", "-", slug)
        slug = slug.strip("-")

        return slug
    



def get_genre_service(
    genre_repo: GenreRepoDep,
    movie_genre_repo: MovieGenreRepoDep,
    movie_repo: MovieRepoDep,
) -> GenreService: 
    return GenreService(genre_repo, movie_genre_repo, movie_repo)

GenreServiceDep = Annotated[GenreService, Depends(get_genre_service)]

