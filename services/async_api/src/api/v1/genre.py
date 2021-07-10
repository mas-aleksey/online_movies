from http import HTTPStatus
from typing import List
from uuid import UUID

from cache.decorator import api_cache
from fastapi import APIRouter, Depends, HTTPException, Path, Request, Response
from models import Genre, ShortGenre
from services import GenreService, get_genre_service

router = APIRouter()


@router.get('/genre', response_model=List[ShortGenre], summary='Возвращает информацию о жанрах')
@api_cache()
async def get_genres(
        request: Request,
        response: Response,
        service: GenreService = Depends(get_genre_service)
) -> List[ShortGenre]:
    genres = await service.get_genres()
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genres not found')
    return genres


@router.get('/genre/{genre_id}', response_model=Genre, summary='Возвращает информацию по жанру')
@api_cache()
async def get_genre(
        request: Request,
        response: Response,
        genre_id: UUID = Path(default=None, description='ID жанра'),
        service: GenreService = Depends(get_genre_service)
) -> Genre:
    genre = await service.get_genre_by_id(str(genre_id))
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')
    return genre
