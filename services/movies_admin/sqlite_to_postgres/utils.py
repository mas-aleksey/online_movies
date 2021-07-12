import json
import sqlite3
from contextlib import contextmanager
from enum import Enum
from os import environ
from typing import Optional, List

DSN = {
    'dbname': environ.get('DATABASE_NAME'),
    'user': environ.get('DATABASE_USER'),
    'password': environ.get('DATABASE_PASSWORD'),
    'host': environ.get('DATABASE_HOST'),
    'port': environ.get('DATABASE_PORT'),
}


class Profession(Enum):
    ACTOR = 'actor'
    DIRECTOR = 'director'
    WRITER = 'writer'


@contextmanager
def sqlite_context(db_path: str):
    _conn = sqlite3.connect(db_path)
    _conn.row_factory = dict_factory
    yield _conn
    _conn.close()


def dict_factory(cursor: sqlite3.Cursor, row: tuple) -> dict:
    row_dict = {}
    for idx, col in enumerate(cursor.description):
        row_dict[col[0]] = row[idx]
    return row_dict


class MovieInfo:
    def __init__(self, row):
        self._id = row.get('id')
        self._genres = row.get('genre')
        self._directors = row.get('director')
        self._title = row.get('title')
        self._description = row.get('plot')
        self._imdb_rating = row.get('imdb_rating')
        self._actors_names = row.get('actors_names')
        self._actors_ids = row.get('actors_ids')
        self._writers = row.get('writers')
        self.writers = []

    @property
    def description(self) -> Optional[str]:
        return self._description if self._description != 'N/A' else None

    @property
    def genres(self) -> List[str]:
        return self._genres.replace(' ', '').split(',')

    @property
    def imdb_rating(self) -> Optional[float]:
        return float(self._imdb_rating) if self._imdb_rating != 'N/A' else None

    @property
    def directors(self) -> Optional[List[str]]:
        return [x.strip() for x in self._directors.split(',')] if self._directors != 'N/A' else None

    @property
    def actors_names(self) -> List[str]:
        return [x for x in self._actors_names.split(',') if x != 'N/A']

    @property
    def actors(self) -> List[dict]:
        return [
            {'id': _id, 'name': name}
            for _id, name in zip(self._actors_ids.split(','), self._actors_names.split(','))
            if name != 'N/A'
        ]

    @property
    def writers_names(self) -> List[str]:
        return [wr['name'] for wr in self.writers]

    def set_movie_writers(self, writers: dict) -> None:
        writers_set = set()
        for writer in json.loads(self._writers):
            writer_id = writer['id']
            if writers[writer_id]['name'] != 'N/A' and writer_id not in writers_set:
                self.writers.append(writers[writer_id])
                writers_set.add(writer_id)

    def get_pg_item(self) -> dict:
        return {
            'id': self._id,
            'rating': self.imdb_rating,
            'genres': self.genres,
            'title': self._title,
            'description': self.description,
            'directors': self.directors,
            'actors_names': self.actors_names,
            'writers_names': self.writers_names,
            'actors': self.actors,
            'writers': self.writers
        }
