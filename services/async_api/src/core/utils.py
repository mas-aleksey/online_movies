import logging
from enum import Enum


class Sort(Enum):
    ID = 'id'
    TITLE = 'title'
    IMDB_RATING = 'imdb_rating'


class SortOrder(Enum):
    ASC = 'asc'
    DESC = 'desc'


class FilterField(Enum):
    GENRE = 'genre'
    ACTORS = 'actors'
    DIRECTORS = 'directors'
    WRITERS = 'writers'


log_converter = {
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG
}
