FROM python:3.9.2-slim-buster

WORKDIR /opt/app

ENV TZ 'UTC'
ENV PYTHONUNBUFFERED=1

RUN apt update \
    && apt install -y gcc bash \
    && pip3 install --upgrade pip

COPY movies_admin/requirements requirements
RUN pip install --no-cache-dir -r requirements/production.txt

COPY . .

RUN ["chmod", "+x", "./entrypoint.sh"]
ENTRYPOINT ["/opt/app/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi", "-w", "2", "-b", ":8000"]

