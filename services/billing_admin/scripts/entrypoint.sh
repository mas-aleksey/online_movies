#!/usr/bin/env bash

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z "$DB_HOST" "$DB_PORT"; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py migrate --noinput
python manage.py createsuperuser --noinput
python manage.py collectstatic --no-input || true

exec "$@"
