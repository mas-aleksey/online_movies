from functools import lru_cache
from typing import Optional

from fastapi import Depends
from models import Genre, ShortGenre
from storage.base import BaseStorage, get_storage


class GenreService:
    """Содержит бизнес-логику по работе с жанрами"""
    def __init__(self, storage: BaseStorage):
        self.storage = storage

    async def get_genres(self) -> Optional[Genre]:
        """Возвращает все жанры"""
        entities = await self.storage.get_genres()
        return [Genre.parse_obj(genre) for genre in entities] if entities else None

    async def get_genre_by_id(self, genre_id: str) -> Optional[Genre]:
        """Возвращает информацию по id.
        Args:
            genre_id: id жанра
        Returns: объект с информацией
        """
        entity = await self.storage.get_genre_by_id(genre_id)
        return Genre.parse_obj(entity) if entity else None


@lru_cache()
def get_genre_service(
        storage: BaseStorage = Depends(get_storage),
) -> GenreService:
    """Провайдер GenreService.
    С помощью Depends он сообщает, что ему необходимы Redis и Elasticsearch
    Используем lru_cache-декоратор, чтобы создать объект сервиса в едином экземпляре (синглтона)
    """
    return GenreService(storage)
