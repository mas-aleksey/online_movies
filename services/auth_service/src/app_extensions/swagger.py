from flask import Flask
from flasgger import Swagger
from src.settings import DOCS_DIR

swagger = Swagger()


def init_swagger(app: Flask):
    swagger.config['url_prefix'] = '/auth2'
    swagger.template_file = DOCS_DIR.joinpath('template.yml').as_posix()
    swagger.init_app(app)
