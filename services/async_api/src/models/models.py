from datetime import date

from pydantic import BaseModel


class ShortGenre(BaseModel):
    """Класс с краткой информацией о жанре"""
    id: str
    name: str


class Genre(ShortGenre):
    """Класс с полной информацией о жанре"""
    description: str = None


class ShortFilm(BaseModel):
    """Класс с краткой информацией о фильме"""
    id: str
    title: str
    access_type: str
    imdb_rating: float = None


class ShortPerson(BaseModel):
    """Класс с краткой информацией о персоне"""
    id: str
    name: str


class Person(ShortPerson):
    """Класс с полной информацией о персоне"""
    films: list[ShortFilm] = None
    roles: list[str] = None


class Film(ShortFilm):
    """Класс с полной информацией о фильме"""
    type: str = ''
    description: str = None
    file_path: str = None
    creation_date: date = None
    end_date: date = None
    age_rating: str = None
    genre: list[ShortGenre] = None
    actors: list[ShortPerson] = None
    writers: list[ShortPerson] = None
    directors: list[ShortPerson] = None
