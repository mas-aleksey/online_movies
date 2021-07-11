CREATE SCHEMA IF NOT EXISTS content;

CREATE TYPE profession AS ENUM ('actor', 'director', 'writer');

-- Таблица сотрудников

CREATE TABLE IF NOT EXISTS person (
  id uuid NOT NULL PRIMARY KEY,
  name VARCHAR(255) NOT NULL
);
CREATE UNIQUE INDEX "person_unique_idx" ON "person" ("name");

-- Таблица жанров

CREATE TABLE IF NOT EXISTS genre (
  id uuid NOT NULL PRIMARY KEY,
  name VARCHAR(50) NOT NULL
);
CREATE UNIQUE INDEX "genre_unique_idx" ON "genre" ("name");

-- Таблица кинопроизведений

CREATE TABLE IF NOT EXISTS filmwork (
    id uuid NOT NULL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    rating FLOAT
);

-- Таблица связей кинопроизведений и сотрудников

CREATE TABLE IF NOT EXISTS filmwork_persons (
    id serial NOT NULL PRIMARY KEY,
    filmwork_id uuid NOT NULL,
    person_id uuid NOT NULL,
    role profession NOT NULL
);
CREATE UNIQUE INDEX "filmwork_person_idx" ON "filmwork_persons" ("filmwork_id", "person_id", "role");

ALTER TABLE "filmwork_persons" ADD CONSTRAINT "filmwork_persons_fk_filmwork_id"
	FOREIGN KEY ("filmwork_id") REFERENCES "filmwork" ("id") ON DELETE CASCADE;

ALTER TABLE "filmwork_persons" ADD CONSTRAINT "filmwork_persons_fk_person_id"
	FOREIGN KEY ("person_id") REFERENCES "person" ("id") ON DELETE CASCADE;

-- Таблица связей кинопроизведений и жанров

CREATE TABLE IF NOT EXISTS filmwork_genres (
    id serial NOT NULL PRIMARY KEY,
    filmwork_id uuid NOT NULL,
    genre_id uuid NOT NULL
);
CREATE UNIQUE INDEX "filmwork_genre_idx" ON "filmwork_genres" ("filmwork_id", "genre_id");

ALTER TABLE "filmwork_genres" ADD CONSTRAINT "filmwork_genres_fk_filmwork_id"
	FOREIGN KEY ("filmwork_id") REFERENCES "filmwork" ("id") ON DELETE CASCADE;

ALTER TABLE "filmwork_genres" ADD CONSTRAINT "filmwork_genres_fk_genre_id"
	FOREIGN KEY ("genre_id") REFERENCES "genre" ("id") ON DELETE CASCADE;


