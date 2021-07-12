FROM python:3.9-slim
EXPOSE 5000

ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.1.2 \
    POETRY_VIRTUALENVS_CREATE="false"

WORKDIR /src

RUN pip install "poetry==$POETRY_VERSION"

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-ansi --no-dev

COPY . ./

CMD ["/bin/sh", "-c", "flask db upgrade && gunicorn --worker-class gevent --workers 2 --bind 0.0.0.0:5000 main:flask_app"]
