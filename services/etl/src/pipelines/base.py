import datetime as dt
import logging
from time import sleep
from typing import Generator, List

from src.es_loader import ESLoader
from src.pg_producer import PgProducer
from src.settings import ETL_SYNC_DELAY, MODE_ETL, VERY_OLD_DATE, ModeEtl
from src.state import State
from src.utils import coroutine


class BasePipeline:
    index: str = ''

    def __init__(self, state: State, db_adapter: PgProducer, es_loader: ESLoader):
        self.state = state
        self.db_adapter = db_adapter
        self.es_loader = es_loader
        self.logger = logging.getLogger(self.__class__.__name__)
        self.state_key = f'{MODE_ETL.value}_last_updated_dt'

    def etl_process(self) -> None:
        """ Метод, который нужно переопределить в дочерних классах. """
        raise NotImplementedError

    def transform(self, target: Generator) -> None:
        """ Метод, который нужно переопределить в дочерних классах. """
        raise NotImplementedError

    @coroutine
    def enrich(self, query: str, target: Generator) -> Generator:
        context = []
        ids = set()
        while True:
            if MODE_ETL == ModeEtl.FILMWORK_ETL:
                fw_ids_from_person = (yield)
                ids.update(fw_ids_from_person)
                self.logger.info('got \'%s\' film_work ids from person etl', len(fw_ids_from_person))

                fw_ids_from_genre = (yield)
                ids.update(fw_ids_from_genre)
                self.logger.info('got \'%s\' film_work ids from genre etl', len(fw_ids_from_genre))

                fw_ids_from_fw = (yield)
                ids.update(fw_ids_from_fw)
                self.logger.info('got \'%s\' film_work ids from film_work etl', len(fw_ids_from_fw))

                self.logger.info('total unique film_work ids to update: \'%s\'', len(ids))
            else:
                ids = (yield)
                self.logger.info('got \'%s\' ids', len(ids))
            if ids:
                for chanck_rows in self.db_adapter.execute(query, list(ids)):
                    context.extend(chanck_rows)

                target.send(context)
                ids.clear()
                context.clear()

    @coroutine
    def collect_updated_ids(self, query: str, target: Generator) -> Generator:
        result = []
        while True:
            query_args = (yield)
            if query_args:
                for chanck_rows in self.db_adapter.execute(query, query_args):
                    result.extend([row['id'] for row in chanck_rows])

            target.send(result)
            result.clear()

    @coroutine
    def es_loader_coro(self, index_name: str) -> Generator:
        while rows := (yield):
            self.es_loader.load_to_es(rows, index_name)

    def event_loop(self, generators: List[Generator]):
        while True:
            sync_start_dt = dt.datetime.now()
            state_value = self.state.get_state(self.state_key) or VERY_OLD_DATE
            self.logger.info('Start ETL process for %s: %s', self.state_key, state_value)
            for generator in generators:
                generator.send(state_value)
            self.state.set_state(self.state_key, str(sync_start_dt))
            self.logger.info('ETL process is finished.  sleep: %s', ETL_SYNC_DELAY)
            sleep(ETL_SYNC_DELAY)
