from functools import lru_cache
from typing import List, Optional

from fastapi import Depends
from models import Person, ShortFilm, ShortPerson
from storage.base import BaseStorage, get_storage


class PersonService:
    """Содержит бизнес-логику по работе с персонами"""
    def __init__(self, storage: BaseStorage):
        self.storage = storage

    async def get_person_by_id(self, person_id: str) -> Optional[Person]:
        """Возвращает информацию по id.
        Args:
            person_id: id персоны
        Returns: объект с информацией
        """
        entity = await self.storage.get_person_by_id(person_id)
        return Person.parse_obj(entity) if entity else None

    async def get_person_films(self, person_id: str) -> Optional[List[Person]]:
        """Возвращает фильмы, в которых участвует персона
        Args:
            person_id: id персоны
        Returns: Список фильмов
        """
        entities = await self.storage.get_person_by_id(person_id)
        return [ShortFilm.parse_obj(film) for film in entities.get('films')] if entities else None

    async def person_search(
            self,
            limit: int,
            page: int,
            query: str
    ) -> Optional[List[ShortFilm]]:
        """Возвращает результат поиска
        Args:
            query: строка для поиска
            page: номер страницы
            limit: количество записей на страницу
        Returns: список персон
        """
        entities = await self.storage.person_search(limit, page, query)
        return [Person.parse_obj(entity) for entity in entities] if entities else None


@lru_cache()
def get_person_service(
        storage: BaseStorage = Depends(get_storage),
) -> PersonService:
    """Провайдер PersonService.
    С помощью Depends он сообщает, что ему необходим Elasticsearch
    Используем lru_cache-декоратор, чтобы создать объект сервиса в едином экземпляре (синглтона)
    """
    return PersonService(storage)
