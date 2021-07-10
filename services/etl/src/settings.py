from os import environ
from enum import Enum


class ModeEtl(Enum):
    FILMWORK_ETL = 'FILMWORK_ETL'
    PERSON_ETL = 'PERSON_ETL'
    GENRE_ETL = 'GENRE_ETL'


DSN = {
    'dbname': environ.get('DATABASE_NAME'),
    'user': environ.get('DATABASE_USER'),
    'password': environ.get('DATABASE_PASSWORD'),
    'host': environ.get('DATABASE_HOST'),
    'port': environ.get('DATABASE_PORT'),
    'options': '-c search_path=content'
}

MODE_ETL = ModeEtl(environ.get('MODE_ETL')) or ModeEtl.FILMWORK_ETL
VERY_OLD_DATE = environ.get('VERY_OLD_DATE') or '2019-01-01 00:00:00'

ELASTIC_HOSTS = environ.get('ELASTIC_HOSTS', 'http://elasticsearch:9200').split(',')

FILE_STORAGE = environ.get('FILE_STORAGE') or 'state.txt'
ETL_SYNC_DELAY = int(environ.get('ETL_SYNC_DELAY', '10'))

LAST_FW_QUERY = "SELECT id FROM filmwork WHERE modified > %s ORDER BY modified;"
LAST_PERSON_QUERY = "SELECT id FROM person WHERE modified > %s ORDER BY modified;"
LAST_GENRE_QUERY = "SELECT id FROM genre WHERE modified > %s ORDER BY modified;"

PERSON_FW_QUERY = '''
SELECT DISTINCT fw.id
FROM filmwork fw
LEFT JOIN filmwork_persons pfw ON pfw.filmwork_id = fw.id
WHERE pfw.person_id IN %s; 
'''

GENRE_FW_QUERY = '''
SELECT DISTINCT fw.id
FROM filmwork fw
LEFT JOIN filmwork_genres gfw ON gfw.filmwork_id = fw.id
WHERE gfw.genre_id IN %s; 
'''

FW_QUERY = '''
SELECT
    fw.id as fw_id, 
    fw.title, 
    fw.description, 
    fw.rating, 
    fw.type, 
    fw.access_type, 
    fw.creation_date, 
    fw.end_date,
    fw.age_limit,
    fw.file_path,
    fw.modified, 
    pfw.role as person_role, 
    p.id as person_id, 
    p.name as person_name,
    g.id as genre_id,
    g.name as genre_name
FROM filmwork fw
LEFT JOIN filmwork_persons pfw ON pfw.filmwork_id = fw.id
LEFT JOIN person p ON p.id = pfw.person_id
LEFT JOIN filmwork_genres gfw ON gfw.filmwork_id = fw.id
LEFT JOIN genre g ON g.id = gfw.genre_id
WHERE fw.id IN %s; 
'''

PERSON_QUERY = '''
SELECT
    p.id as person_id,
    p.name as person_name,
    pfw.role as person_role,
    fw.id as fw_id,
    fw.title as fw_title,
    fw.rating as fw_rating
FROM person p
LEFT JOIN filmwork_persons pfw ON pfw.person_id = p.id
LEFT JOIN filmwork fw ON fw.id = pfw.filmwork_id
WHERE p.id IN %s; 
'''


GENRE_QUERY = '''
SELECT
    g.id as genre_id,
    g.name as genre_name,
    g.description as genre_description
FROM genre g
WHERE g.id IN %s; 
'''