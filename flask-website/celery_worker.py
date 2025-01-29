from flaskr import create_app

"""
On linux, this celery_worker can be run with
  celery -A celery_worker worker --loglevel INFO


On windows, this celery_worker can be run with
  celery -A celery_worker worker --loglevel INFO --pool gevent

Needing gevent, see https://github.com/sumanentc/fastapi-celery-rabbitmq-application/issues/1
"""

flask_app = create_app()
celery = flask_app.extensions['celery']
