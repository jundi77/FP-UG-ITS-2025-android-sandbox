import sqlite3
from datetime import datetime

import click
from flask import current_app, g
from werkzeug.security import generate_password_hash
from flaskr.utils.db import DB

sqlite3.register_converter(
    # "timestamp", lambda v: datetime.fromisoformat(v.decode())
    "timestamp", lambda v: str(v.decode())
)

sqlite3.register_converter(
    "boolean", lambda v: bool(int(v.decode()) == 1)
)

def get_db():
    if 'db' not in g:
        """
        i need centralized db retry mechanism if it's locked,
        ansible can get intense in updating db when the task is skipped.
        """
        g.db = DB(
            retries=15,
            delay=0.1, # seconds!
            database=current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

def init_user():
    db = get_db()
    db.execute(
        'INSERT INTO user (username, password) VALUES (?, ?)',
        ('admin', generate_password_hash('admin'))
    )
    db.commit()

def reset_apk():
    db = get_db()
    db.execute(
        'DELETE FROM android_app'
    )
    db.commit()

def reset_queue():
    db = get_db()
    db.execute(
        'DELETE FROM queue_dynamic_analysis_task'
    )
    db.commit()

def reset_dynamic_analysis_task():
    db = get_db()
    db.execute('DELETE FROM dynamic_analysis_app')
    db.execute('DELETE FROM dynamic_analysis_task')
    db.execute('DELETE FROM dynamic_analysis_log')
    db.execute('DELETE FROM queue_dynamic_analysis_task')
    db.execute('UPDATE config SET lock_dynamic_analysis_task_id=NULL')
    db.commit()

@click.command('init-user')
def init_user_command():
    init_user()
    click.echo('User init done.')

@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('DB init done.')

@click.command('reset-apk')
def reset_apk_command():
    reset_apk()
    click.echo('DB android_app table is reset.')

@click.command('reset-analysis')
def reset_dynamic_analysis_task_command():
    reset_dynamic_analysis_task()
    click.echo('DB all dynamic analysis related record is reset.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(init_user_command)
    app.cli.add_command(reset_apk_command)
    app.cli.add_command(reset_dynamic_analysis_task_command)
