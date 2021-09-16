from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import List


@dataclass
class ShortFilm:
    id: str
    title: str
    access_type: str = ''
    imdb_rating: float = None


@dataclass
class ShortPerson:
    id: str
    name: str


@dataclass
class Person(ShortPerson):
    roles: List[str] = field(default_factory=list)
    films: List[ShortFilm] = field(default_factory=list)

    def add_role(self, role: str):
        if role not in self.roles:
            self.roles.append(role)

    def add_film(self, film: ShortFilm):
        if film not in self.films:
            self.films.append(film)

    @property
    def as_dict(self):
        return asdict(self)


@dataclass
class ShortGenre:
    id: str
    name: str


@dataclass
class Genre(ShortGenre):
    description: str

    @property
    def as_dict(self):
        return asdict(self)


@dataclass
class Film(ShortFilm):
    description: str = ''
    type: str = ''
    creation_date: datetime = None
    end_date: datetime = None
    age_rating: str = ''
    file_path: str = ''
    genre: List[ShortGenre] = field(default_factory=list)
    actors: List[ShortPerson] = field(default_factory=list)
    writers: List[ShortPerson] = field(default_factory=list)
    directors: List[ShortPerson] = field(default_factory=list)

    def add_genre(self, gen: ShortGenre):
        if gen not in self.genre:
            self.genre.append(gen)

    def add_person(self, person: ShortPerson, role: str):
        if role == 'actor':
            if person not in self.actors:
                self.actors.append(person)
        elif role == 'writer':
            if person not in self.writers:
                self.writers.append(person)
        elif role == 'director':
            if person not in self.directors:
                self.directors.append(person)

    @property
    def as_dict(self):
        return asdict(self)
