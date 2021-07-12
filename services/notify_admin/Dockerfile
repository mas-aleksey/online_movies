FROM python:3.9-slim

WORKDIR /var/app

ENV FETCH_PACKAGES="wget gnupg2" \
    BUILD_PACKAGES="build-essential gcc linux-headers-amd64 libffi-dev libgeos-c1v5 libpq-dev libssl-dev" \
    PACKAGES="postgresql-client"

RUN apt update && \
    apt install -y ${FETCH_PACKAGES}

RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ stretch-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

RUN apt update && \
    apt upgrade -y && \
    apt install -y --no-install-recommends ${BUILD_PACKAGES} ${PACKAGES} && \
    rm -rf /var/lib/apt/lists/*

ADD . /var/app

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -U pipenv && \
    pipenv install --dev --deploy --system

VOLUME static
ENTRYPOINT ["scripts/entrypoint.sh"]
CMD ["/usr/local/bin/gunicorn", "-c", "gunicorn.py", "config.wsgi:application"]
