FROM python:3.9.2-slim-buster

WORKDIR /opt/app/

ENV TZ 'UTC'
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt update \
    && pip3 install --upgrade pip

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH "${PYTHONPATH}:/opt/app/src"
ENTRYPOINT python src/pywsgi.py