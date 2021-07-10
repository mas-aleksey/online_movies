from typing import Generator

from src.models import Genre
from src.settings import GENRE_QUERY, LAST_GENRE_QUERY
from src.utils import coroutine

from .base import BasePipeline


class GenrePipeline(BasePipeline):
    index = 'genres'

    @coroutine
    def transform(self, target: Generator) -> Generator:
        genre = {}
        while rows := (yield):
            for row in rows:
                if row['genre_id'] not in genre:
                    genre[row['genre_id']] = Genre(
                        row['genre_id'],
                        row['genre_name'],
                        row['genre_description']
                    )
            target.send([genre.as_dict for genre in genre.values()])
            genre.clear()

    def etl_process(self):
        es_target = self.es_loader_coro(self.index)
        transform_target = self.transform(es_target)
        enrich_target = self.enrich(GENRE_QUERY, transform_target)

        updated_genre_target = self.collect_updated_ids(LAST_GENRE_QUERY, enrich_target)

        self.event_loop([updated_genre_target])
