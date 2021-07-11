#!/usr/bin/env bash

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z "$POSTGRES_HOST_NAME" "$POSTGRES_LISTEN_PORT"; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python -m sqlite_to_postgres
cd movies_admin
python manage.py migrate movies --fake-initial --noinput
python manage.py migrate --noinput
python manage.py createsuperuser --noinput
python manage.py collectstatic --noinput
gunicorn config.wsgi -w 2 -b :8000

exec "$@"