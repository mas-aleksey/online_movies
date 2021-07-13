from http import HTTPStatus
from typing import List
from uuid import UUID

from cache.decorator import api_cache
from core.utils import FilterField, Sort, SortOrder
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, Response
from models import Film, ShortFilm
from services import FilmService, get_film_service

router = APIRouter()


@router.get('/film', response_model=List[ShortFilm], summary='Возвращает список фильмов по фильтру')
@api_cache()
async def get_films_by_filter(
        request: Request,
        response: Response,
        limit: int = Query(description='Количество фильмов на страницу', default=50, ge=1, le=100),
        page: int = Query(description='Номер страницы', default=1, ge=1),
        sort: Sort = Query(description='Свойство, по которому нужно отсортировать результат', default=Sort.IMDB_RATING),
        sort_order: SortOrder = Query(description='Порядок сортировки', default=SortOrder.ASC),
        filter_field: FilterField = Query(description='Поле, по которому необходимо фильтровать', default=None),
        filter_query: UUID = Query(description='uid объекта в поле filter', default=None),
        service: FilmService = Depends(get_film_service)
) -> List[ShortFilm]:
    if filter_field and not filter_query:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='filter_query must be set')
    films = await service.get_films_by_filter(
        limit=limit, page=page, roles=request.scope["roles"], sort=sort, sort_order=sort_order,
        filter_field=filter_field, filter_query=filter_query
    )
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')
    return films


@router.get('/film/search', response_model=List[ShortFilm], summary='Возвращает список фильмов по запросу')
@api_cache()
async def get_films_by_search(
        request: Request,
        response: Response,
        limit: int = Query(description='Количество фильмов на страницу', default=50, ge=1, le=100),
        page: int = Query(description='Номер страницы', default=1, ge=1),
        query: str = Query(
            ...,
            description='Неточный поиск по названию, описанию, актёрам, сценаристам и режиссёрам фильма',
            max_length=64
        ),
        service: FilmService = Depends(get_film_service)
) -> List[ShortFilm]:
    films = await service.film_search(limit=limit, page=page, query=query, roles=request.scope["roles"])
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')
    return films


@router.get('/film/{film_id}', response_model=Film, summary='Возвращает информацию по фильму')
@api_cache()
async def get_film_details(
        request: Request,
        response: Response,
        film_id: UUID = Path(default=None, description='ID фильма'),
        service: FilmService = Depends(get_film_service)
) -> Film:
    film = await service.get_film_by_id(str(film_id))
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')
    return film
