from typing import Generator

from src.models import Person, ShortFilm
from src.settings import LAST_PERSON_QUERY, PERSON_QUERY
from src.utils import coroutine

from .base import BasePipeline


class PersonPipeline(BasePipeline):
    index = 'persons'

    @coroutine
    def transform(self, target: Generator) -> Generator:
        people = {}
        while rows := (yield):
            for row in rows:
                if row['person_id'] not in people:
                    people[row['person_id']] = Person(
                        row['person_id'],
                        row['person_name']
                    )
                people[row['person_id']].add_role(row['person_role'])
                people[row['person_id']].add_film(
                    ShortFilm(
                        row['fw_id'],
                        row['fw_title'],
                        row['fw_rating']
                    )
                )
            target.send([person.as_dict for person in people.values()])
            people.clear()

    def etl_process(self):
        es_target = self.es_loader_coro(self.index)
        transform_target = self.transform(es_target)
        enrich_target = self.enrich(PERSON_QUERY, transform_target)

        updated_person_target = self.collect_updated_ids(LAST_PERSON_QUERY, enrich_target)

        self.event_loop([updated_person_target])
