from http import HTTPStatus
from typing import List
from uuid import UUID

from cache.decorator import api_cache
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, Response
from models import Person, ShortFilm
from services import PersonService, get_person_service

router = APIRouter()


@router.get('/person/search', response_model=List[Person], summary='Поиск персон')
@api_cache()
async def get_person_by_search(
        request: Request,
        response: Response,
        limit: int = Query(description='Количество персон на страницу', default=50, ge=1, le=100),
        page: int = Query(description='Номер страницы', default=1, ge=1),
        query: str = Query(..., description='Неточный поиск по имени персоны', max_length=64),
        service: PersonService = Depends(get_person_service)
) -> List[Person]:
    people = await service.person_search(limit=limit, page=page, query=query)
    if not people:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='persons not found')
    return people


@router.get('/person/{person_id}', response_model=Person, summary='Возвращает информацию по персоне')
@api_cache()
async def get_person(
        request: Request,
        response: Response,
        person_id: UUID = Path(default=None, description='ID персоны'),
        service: PersonService = Depends(get_person_service)
) -> Person:
    person = await service.get_person_by_id(str(person_id))
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
    return person


@router.get('/person/{person_id}/film', response_model=List[ShortFilm], summary='Возвращает фильмы по персоне')
@api_cache()
async def get_person_films(
        request: Request,
        response: Response,
        person_id: UUID = Path(default=None, description='ID персоны'),
        service: PersonService = Depends(get_person_service)
) -> List[ShortFilm]:
    person_films = await service.get_person_films(str(person_id))
    if not person_films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person films not found')
    return person_films
