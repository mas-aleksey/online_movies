from typing import List, Optional

import backoff
from core.config import ELASTIC_MOVIES_INDEX, ELASTIC_PERSON_INDEX, ELASTIC_GENRE_INDEX, ELASTIC_HOST, ELASTIC_PORT
from core.utils import FilterField, Sort, SortOrder
from elasticsearch import AsyncElasticsearch, exceptions
from storage.base import BaseStorage


class ElasticStorage(BaseStorage):
    def __init__(self):
        self.movies_index = ELASTIC_MOVIES_INDEX
        self.genre_index = ELASTIC_GENRE_INDEX
        self.person_index = ELASTIC_PERSON_INDEX

    async def get_film_by_id(self, film_id: str) -> Optional[dict]:
        return await self._get_by_id(self.movies_index, film_id)

    async def get_genre_by_id(self, genre_id: str) -> Optional[dict]:
        return await self._get_by_id(self.genre_index, genre_id)

    async def get_person_by_id(self, person_id: str) -> Optional[dict]:
        return await self._get_by_id(self.person_index, person_id)

    async def get_genres(self) -> Optional[List[dict]]:
        return await self._search(self.genre_index)

    async def film_search(self, limit: int, page: int, query: str, roles: list) -> Optional[List[dict]]:
        body = {
            "size": limit,
            "from": (page - 1) * limit,
            "query": {
                "bool": {
                    "filter": {"terms": {"access_type": roles}}
                }
            }
        }
        if query:
            body['query']['bool']['must'] = {
                "multi_match": {
                    "query":  query,
                    "fuzziness": "auto",
                    "fields": [
                        "title^5",
                        "description^4",
                        "actors^3",
                        "writers^2",
                        "directors^2"
                    ]
                }
            }
        return await self._search(self.movies_index, body)

    async def get_films_by_filter(
            self,
            limit: int,
            page: int,
            roles: list,
            sort: Sort = None,
            sort_order: SortOrder = None,
            filter_field: FilterField = None,
            filter_query: str = None,
    ) -> Optional[List[dict]]:
        body = {
            "size": limit,
            "from": (page - 1) * limit,
            "query": {
                "bool": {"filter": {"terms": {"access_type": roles}}}
            }
        }
        if sort and sort_order:
            sort = 'title.raw' if sort.value == 'title' else sort.value
            body['sort'] = {
                sort: sort_order.value
            }
        if filter_field and filter_query:
            body['query']['bool']['must'] = {
                "nested": {
                    "path": filter_field.value,
                    "query": {
                        "bool": {
                            "must": [
                                {"match": {f'{filter_field.value}.id':  filter_query}}
                            ]
                        }
                    }
                }
            }
        return await self._search(self.movies_index, body)

    async def person_search(self, limit: int, page: int, query: str) -> Optional[List[dict]]:
        query_string = ' '.join([f'{sub}~' for sub in query.split()])
        body = {
            "size": limit,
            "from": (page - 1) * limit,
            "query": {
                "query_string": {
                    "default_field": "name",
                    "query": query_string
                }
            }
        }
        return await self._search(self.person_index, body)

    async def open_connection(self):
        self.elastic = AsyncElasticsearch(hosts=[f'{ELASTIC_HOST}:{ELASTIC_PORT}'])

    async def close_connection(self):
        if self.elastic:
            await self.elastic.close()
        self.elastic = None

    @backoff.on_exception(backoff.expo, exceptions.ConnectionError, max_tries=10)
    async def _get_by_id(self, index_name: str, entity_id: str) -> Optional[dict]:
        try:
            hit = await self.elastic.get(index=index_name, id=entity_id)
            return hit.get('_source')
        except exceptions.NotFoundError:
            return None

    @backoff.on_exception(backoff.expo, exceptions.ConnectionError, max_tries=10)
    async def _search(self, index_name: str, body: dict = None) -> Optional[List[dict]]:
        try:
            doc = await self.elastic.search(index=index_name, body=body)
            return [hit.get('_source') for hit in doc.get('hits', {}).get('hits', {})]
        except exceptions.NotFoundError:
            return None
