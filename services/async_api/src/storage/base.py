from abc import ABC, abstractmethod
from typing import Optional, List
from core.utils import Sort, SortOrder, FilterField


class BaseStorage(ABC):
    @abstractmethod
    async def get_film_by_id(self, film_id) -> Optional[dict]:
        """Возвращает фильм по id"""
        pass

    @abstractmethod
    async def get_genre_by_id(self, genre_id) -> Optional[dict]:
        """Возвращает жанр по id"""
        pass

    @abstractmethod
    async def get_person_by_id(self, person_id) -> Optional[dict]:
        """Возвращает персону по id"""
        pass

    @abstractmethod
    async def film_search(self, limit: int, page: int, query: str) -> Optional[List[dict]]:
        """Поиск фильмов по запросу
            Args:
                page: номер страницы
                limit: количество записей на страницу
                query: неточный поиск
            Returns: список словарей
            """
        pass

    @abstractmethod
    async def get_films_by_filter(
            self,
            limit: int,
            page: int,
            sort: Sort,
            sort_order: SortOrder,
            filter_field: FilterField,
            filter_query: str,
    ) -> Optional[List[dict]]:
        """Поиск фильмов по фильтру
            Args:
                filter_query: uuid для поиска фильтру
                filter_field: поле, по которому необходимо фильтровать
                sort_order: порядок сортировки
                sort: поле, по которому необходимо сортировать
                page: номер страницы
                limit: количество записей на страницу
            Returns: список словарей
            """
        pass

    @abstractmethod
    async def get_genres(self) -> Optional[List[dict]]:
        """Возвращает все жанры"""
        pass

    @abstractmethod
    async def person_search(self, limit: int, page: int, query: str) -> Optional[List[dict]]:
        """Поиск персон по запросу
        Args:
            query: неточный поиск
            page: номер страницы
            limit: количество записей на страницу
        Returns: список словарей
        """
        pass

    @abstractmethod
    async def open_connection(self):
        """
        Открывает соединение с хранилищем
        """
        pass

    @abstractmethod
    async def close_connection(self):
        """
        Закрывает соединение с хранилищем
        """
        pass


storage: BaseStorage = None


def get_storage() -> BaseStorage:
    return storage
