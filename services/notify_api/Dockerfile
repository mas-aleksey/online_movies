FROM python:3.9.2-slim-buster

WORKDIR /src

ENV TZ 'UTC'
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt update \
    && apt install -y gcc bash \
    && pip3 install --upgrade pip

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./src .

ENTRYPOINT uvicorn main:app --host 0.0.0.0 --port 8000