from functools import lru_cache
from typing import List, Optional

from core.utils import Sort, SortOrder, FilterField
from fastapi import Depends
from models import Film, ShortFilm
from storage.base import BaseStorage, get_storage


class FilmService:
    """Содержит бизнес-логику по работе с фильмами"""
    def __init__(self, storage: BaseStorage):
        self.storage = storage

    async def get_film_by_id(self, film_id: str) -> Optional[Film]:
        """Возвращает информацию по id.
        Args:
            film_id: id фильма
        Returns: объект с информацией
        """
        entity = await self.storage.get_film_by_id(film_id)
        return Film.parse_obj(entity) if entity else None

    async def film_search(self, limit: int, page: int, query: str, roles: list) -> Optional[List[ShortFilm]]:
        """Поиск по запросу
        Args:
            query: строка для поиска
            page: номер страницы
            limit: количество записей на страницу
            roles: список ролей пользователя
        Returns: список фильмов
        """
        entities = await self.storage.film_search(limit, page, query, roles)
        return [ShortFilm.parse_obj(entity) for entity in entities] if entities else None

    async def get_films_by_filter(
            self,
            limit: int,
            page: int,
            roles: list,
            sort: Sort = None,
            sort_order: SortOrder = None,
            filter_field: FilterField = None,
            filter_query: str = None
    ) -> Optional[List[ShortFilm]]:
        """Поиск по фильтру
        Args:
            limit: количество записей на страницу
            page: номер страницы
            roles: список ролей пользователя
            filter_query: uuid для поиска фильтру
            filter_field: поле, по которому необходимо фильтровать
            sort_order: порядок сортировки
            sort: поле, по которому необходимо сортировать
        Returns: список фильмов
        """
        entities = await self.storage.get_films_by_filter(
            limit, page, roles, sort, sort_order, filter_field, filter_query
        )
        return [ShortFilm.parse_obj(entity) for entity in entities] if entities else None


@lru_cache()
def get_film_service(
        storage: BaseStorage = Depends(get_storage),
) -> FilmService:
    """Провайдер FilmService.
    С помощью Depends он сообщает, что ему необходим Elasticsearch
    Используем lru_cache-декоратор, чтобы создать объект сервиса в едином экземпляре (синглтона)
    """
    return FilmService(storage)
