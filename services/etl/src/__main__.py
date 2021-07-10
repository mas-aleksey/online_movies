import logging

from src.pipelines.film_etl import FilmWorkPipeline
from src.pipelines.genre_etl import GenrePipeline
from src.pipelines.person_etl import PersonPipeline

from src.es_loader import ESLoader
from src.pg_producer import PgProducer
from src.settings import DSN, ELASTIC_HOSTS, FILE_STORAGE, MODE_ETL, ModeEtl
from src.state import JsonFileStorage, State

logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('root')


if __name__ == '__main__':
    logger.info('Start ETL application with %s mode', MODE_ETL.value)
    jsf = JsonFileStorage(FILE_STORAGE)
    state = State(jsf)
    db_adapter = PgProducer(DSN)
    es_loader = ESLoader(ELASTIC_HOSTS)

    if MODE_ETL == ModeEtl.FILMWORK_ETL:
        filmwork = FilmWorkPipeline(state, db_adapter, es_loader)
        filmwork.etl_process()
    elif MODE_ETL == ModeEtl.PERSON_ETL:
        person = PersonPipeline(state, db_adapter, es_loader)
        person.etl_process()
    elif MODE_ETL == ModeEtl.GENRE_ETL:
        genre = GenrePipeline(state, db_adapter, es_loader)
        genre.etl_process()
