import os
from flask import Flask
from celery import Celery, Task

def init_celery(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args, **kwargs) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery = Celery(
        app.name,
        task_cls=FlaskTask,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL'],
    )

    celery.set_default()
    app.extensions['celery'] = celery

    return celery

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    celery_db = os.path.join(app.instance_path, 'celery.sqlite')
    celery_db_result = os.path.join(app.instance_path, 'celery_results.sqlite')

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        UPLOAD_FOLDER=os.path.join(app.instance_path, 'uploads'),
        WEBSOCKIFY_TOKEN_FOLDER=os.path.join(app.instance_path, 'websockify-token'),

        # https://docs.celeryq.dev/en/stable/userguide/configuration.html#conf-database-result-backend
        CELERY_BROKER_URL=f'sqla+sqlite:///{celery_db}',

        # https://celery-safwan.readthedocs.io/en/latest/userguide/configuration.html#rpc-backend-settings
        CELERY_RESULT_BACKEND=f'db+sqlite:///{celery_db_result}',
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_pyfile(test_config)
    
    init_celery(app)
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    try:
        os.makedirs(app.config['UPLOAD_FOLDER'])
    except OSError:
        pass

    try:
        os.makedirs(app.config['WEBSOCKIFY_TOKEN_FOLDER'])
    except OSError:
        pass
    
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)


    from . import api
    app.register_blueprint(api.bp)

    from . import watcher
    app.register_blueprint(watcher.bp)
    app.add_url_rule('/', endpoint='index')

    return app