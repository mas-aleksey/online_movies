FROM python:3.9

WORKDIR /var/app

ENV FETCH_PACKAGES="wget gnupg2" \
    BUILD_PACKAGES="build-essential autoconf libtool pkg-config \
    gcc linux-headers-amd64 libffi-dev libgeos-c1v5 libpq-dev libssl-dev python3-dev libgnutls28-dev" \
    PACKAGES="postgresql-client"

RUN apt update && \
    apt install -y ${FETCH_PACKAGES}

RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ stretch-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

RUN apt update && \
    apt upgrade -y && \
    apt install -y --no-install-recommends ${BUILD_PACKAGES} ${PACKAGES} && \
    rm -rf /var/lib/apt/lists/*

COPY requirements ./requirements

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -U pipenv && \
    pip install --no-cache-dir -r /var/app/requirements/production.txt

ADD . /var/app

VOLUME /var/app/static
RUN ["chmod", "+x", "./scripts/entrypoint.sh"]
ENTRYPOINT ["/var/app/scripts/entrypoint.sh"]
ENV PYTHONPATH "/opt/app"
CMD ["gunicorn", "config.wsgi", "-w", "2", "-b", ":8000"]
