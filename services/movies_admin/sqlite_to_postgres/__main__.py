import sqlite3
from os import path
from pathlib import Path
from typing import List, Optional
import logging
import uuid
import psycopg2

from psycopg2.extras import DictCursor
from .utils import sqlite_context, Profession, DSN, MovieInfo


LOGGER = logging.getLogger(__name__)
CURR_DIR = Path(__file__).resolve(strict=True).parent
SELECT_MOVIES_AND_ACTORS_QUERY = '''
WITH x as (
    SELECT m.id, group_concat(a.id) as actors_ids, group_concat(a.name) as actors_names
    FROM movies m
             LEFT JOIN movie_actors ma on m.id = ma.movie_id
             LEFT JOIN actors a on ma.actor_id = a.id
    GROUP BY m.id
)
SELECT m.id, genre, director, title, plot, imdb_rating, x.actors_ids, x.actors_names,
       CASE
        WHEN m.writers = '' THEN '[{"id": "' || m.writer || '"}]'
        ELSE m.writers
       END AS writers
FROM movies m
LEFT JOIN x ON m.id = x.id;
'''
SELECT_WRITERS_QUERY = 'SELECT DISTINCT id, name FROM writers;'


class PGLoader:
    def __init__(self, _dsn: dict):
        self.dsn = _dsn
        self.person_map = {}
        self.genre_map = {}

    def prepare_db(self, cursor: DictCursor) -> None:
        init_sql = CURR_DIR / 'init.sql'
        with open(init_sql) as file:
            query = file.read()
        cursor.execute(query)

    def pre_load_maps(self, cursor: DictCursor) -> None:
        cursor.execute("SELECT id, name FROM genre;")
        for genre in cursor.fetchall():
            self.genre_map[genre['name']] = genre['id']

        cursor.execute("SELECT id, name FROM person;")
        for person in cursor.fetchall():
            self.person_map[person['name']] = person['id']

    def load_filmworks_to_pg(self, records: List[dict]) -> None:
        with psycopg2.connect(**self.dsn) as _conn, _conn.cursor(cursor_factory=DictCursor) as cursor:
            self.prepare_db(cursor)
            self.pre_load_maps(cursor)
            for record in records:
                film_uuid = self.save_filmwork(cursor, record['title'], record['description'], record['rating'])
                self.save_genres(cursor, film_uuid, record['genres'])
                self.save_people(cursor, film_uuid, record['actors_names'], Profession.ACTOR.value)
                self.save_people(cursor, film_uuid, record['directors'], Profession.DIRECTOR.value)
                self.save_people(cursor, film_uuid, record['writers_names'], Profession.WRITER.value)

    def save_genres(self, cursor: DictCursor, film_uuid: str, genres: List[str]) -> None:
        new_genres_to_insert = []
        links_to_insert = []
        for genre in genres:
            if genre not in self.genre_map:
                genre_uuid = str(uuid.uuid4())
                self.genre_map[genre] = genre_uuid
                new_genres_to_insert.append((genre_uuid, genre))
                links_to_insert.append((film_uuid, genre_uuid))
            else:
                links_to_insert.append((film_uuid, self.genre_map[genre]))

        if new_genres_to_insert:
            genre_args = ','.join(cursor.mogrify("(%s, %s)", item).decode() for item in new_genres_to_insert)
            cursor.execute(f"INSERT INTO genre (id, name) VALUES {genre_args}")

        if links_to_insert:
            link_args = ','.join(cursor.mogrify("(%s, %s)", item).decode() for item in links_to_insert)
            cursor.execute(f"INSERT INTO filmwork_genres (filmwork_id, genre_id) VALUES {link_args}")

    def save_people(self, cursor: DictCursor, film_uuid: str, names: List[str], role: str) -> None:

        if not names:
            return

        new_people_to_insert = []
        links_to_insert = []
        for name in set(names):
            if name not in self.person_map:
                person_uuid = str(uuid.uuid4())
                self.person_map[name] = person_uuid
                new_people_to_insert.append((person_uuid, name))
                links_to_insert.append((film_uuid, person_uuid, role))
            else:
                links_to_insert.append((film_uuid, self.person_map[name], role))

        if new_people_to_insert:
            person_args = ','.join(cursor.mogrify("(%s, %s)", item).decode() for item in new_people_to_insert)
            cursor.execute(f"INSERT INTO person (id, name) VALUES {person_args}")

        if links_to_insert:
            link_args = ','.join(cursor.mogrify("(%s, %s, %s)", item).decode() for item in links_to_insert)
            cursor.execute(f"INSERT INTO filmwork_persons (filmwork_id, person_id, role) VALUES {link_args}")

    @staticmethod
    def save_filmwork(cursor: DictCursor, title: str, description: Optional[str], rating: Optional[float]) -> str:
        film_uuid = str(uuid.uuid4())
        film_data = (film_uuid, title, description, rating)
        cursor.execute(
            "INSERT INTO filmwork (id, title, description, rating) VALUES (%s, %s, %s, %s)", film_data
        )
        return film_uuid


class ETL:
    def __init__(self, _conn: sqlite3.Connection, pg_loader: PGLoader):
        self.pg_loader = pg_loader
        self.conn = _conn

    def load_writers_names(self) -> dict:
        writers = {}
        for writer in self.conn.execute(SELECT_WRITERS_QUERY):
            writers[writer['id']] = writer
        return writers

    @staticmethod
    def prepare_row(row, writers) -> dict:
        movie_info = MovieInfo(row)
        movie_info.set_movie_writers(writers)
        return movie_info.get_pg_item()

    def load(self):
        records = []
        writers = self.load_writers_names()

        for row in self.conn.execute(SELECT_MOVIES_AND_ACTORS_QUERY):
            prepared_row = self.prepare_row(row, writers)
            records.append(prepared_row)

        self.pg_loader.load_filmworks_to_pg(records)


if __name__ == "__main__":
    try:
        loader = PGLoader(DSN)
        sqlite_path = path.join(path.dirname(__file__), 'db.sqlite')
        with sqlite_context(sqlite_path) as conn:
            etl = ETL(conn, loader)
            etl.load()
    except Exception as e:  # noqa
        print(f'ETL Failed: {e}')
    else:
        print('ETL finished')
