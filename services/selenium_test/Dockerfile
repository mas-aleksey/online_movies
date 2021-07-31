FROM python:3.7-alpine3.10

WORKDIR /opt/app/

RUN chmod 777 -R /opt/

ENV TZ 'UTC'
ENV PYTHONUNBUFFERED=1

RUN apk update \
    && apk add --no-cache libpq tzdata libffi git psutils \
    && python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir -U pip==19.1.1 setuptools==41.2.0 setuptools-scm==3.3.3

COPY requirements.txt requirements.txt

RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Update apk repo
RUN echo "https://dl-4.alpinelinux.org/alpine/v3.10/main" >> /etc/apk/repositories && \
    echo "https://dl-4.alpinelinux.org/alpine/v3.10/community" >> /etc/apk/repositories

RUN apk add chromium chromium-chromedriver

RUN pip install --no-cache-dir -r requirements.txt


COPY . .

ENTRYPOINT  ["/opt/venv/bin/python", "-m", "pytest", "-vv", "-s", "--alluredir=allure-results"]