import datetime
import logging

import pytest
import pytz

from app import create_app, db, app

BASE_URL = 'http://localhost:5000/api/v1'
FLASK_APP = None

@pytest.fixture
def flask_app():
    try:
        _app = create_app()
    except:
        _app = app

    _app.config["TESTING"] = True
    _app.testing = True

    _app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://django:django@localhost:5432/ya_auth"

    with _app.app_context():
        db.create_all()
    yield _app
    with _app.app_context():
        db.drop_all()


@pytest.fixture
def client(flask_app):
    client = flask_app.test_client()
    yield client
