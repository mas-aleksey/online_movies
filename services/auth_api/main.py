# from gevent import monkey
#
# monkey.patch_all()

from app import create_app

flask_app = create_app()
