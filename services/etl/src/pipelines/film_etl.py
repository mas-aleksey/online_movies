from typing import Generator

from src.models import Film, ShortGenre, ShortPerson
from src.settings import (
    FW_QUERY, GENRE_FW_QUERY, LAST_FW_QUERY,
    LAST_GENRE_QUERY, LAST_PERSON_QUERY, PERSON_FW_QUERY,
)
from src.utils import coroutine
from .base import BasePipeline


class FilmWorkPipeline(BasePipeline):
    index = 'movies'

    @coroutine
    def transform(self, target: Generator) -> Generator:
        movies = {}
        while rows := (yield):
            for row in rows:
                if row['fw_id'] not in movies:
                    movies[row['fw_id']] = Film(
                        row['fw_id'],
                        row['title'],
                        row['rating'],
                        row['description'],
                        row['type'],
                        row['access_type'],
                        row['creation_date'],
                        row['end_date'],
                        row['age_limit'],
                        row['file_path']
                    )
                movies[row['fw_id']].add_genre(
                    ShortGenre(row['genre_id'], row['genre_name'])
                )
                movies[row['fw_id']].add_person(
                    ShortPerson(row['person_id'], row['person_name']),
                    row['person_role']
                )
            target.send([movie.as_dict for movie in movies.values()])
            movies.clear()

    def etl_process(self):
        es_target = self.es_loader_coro(self.index)
        transform_target = self.transform(es_target)
        enrich_target = self.enrich(FW_QUERY, transform_target)

        person_fw_target = self.collect_updated_ids(PERSON_FW_QUERY, enrich_target)
        genre_fw_target = self.collect_updated_ids(GENRE_FW_QUERY, enrich_target)

        updated_fw_target = self.collect_updated_ids(LAST_FW_QUERY, enrich_target)
        updated_person_target = self.collect_updated_ids(LAST_PERSON_QUERY, person_fw_target)
        updated_genre_target = self.collect_updated_ids(LAST_GENRE_QUERY, genre_fw_target)

        self.event_loop([updated_person_target, updated_genre_target, updated_fw_target])
