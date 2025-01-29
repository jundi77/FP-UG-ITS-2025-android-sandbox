from flask import (
    g, current_app
)
from uuid import uuid4
from flaskr.db import get_db
import os
import pyaxmlparser

def list_uploaded_apps():
    return get_db().execute(
        'SELECT * FROM android_app WHERE user_id = ? and is_deleted = 0 ORDER BY id',
        (g.user['id'],)
    ).fetchall()

def list_visible_uploaded_apps():
    return get_db().execute(
        'SELECT * FROM android_app WHERE user_id = ? and is_deleted = 0 and is_hidden_dynamic_analysis_task = 0 ORDER BY id',
        (g.user['id'],)
    ).fetchall()

def get_app_details(app_id):
    return get_db().execute(
        'SELECT * FROM android_app WHERE id = ?',
        (app_id,)
    ).fetchone()

def save_uploaded_app(app_file):
    saved_filename = str(uuid4())
    saved_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], saved_filename)
    app_file.save(saved_filepath)

    try:
        apk = pyaxmlparser.APK(saved_filepath)
    except Exception as e:
        os.remove(saved_filepath)
        return False

    if not apk.is_valid_APK():
        os.remove(saved_filepath)
        return False

    app_name = apk.application
    package_name = apk.package
    if app_name == '': app_name = '(empty)'

    db = get_db()
    db.execute(
        'INSERT INTO android_app (user_id, app_name, package_name, filename) VALUES (?, ?, ?, ?)',
        (g.user['id'], app_name, package_name, saved_filename,)
    )
    db.commit()
    return True

def soft_delete_uploaded_app(app_id):
    db = get_db()
    db.execute(
        'UPDATE android_app SET is_deleted = 1'
        ' WHERE id = ?',
        (app_id,)
    )
    db.commit()

    return True

def toggle_hide_uploaded_app(app_id):
    db = get_db()
    db.execute(
        'UPDATE android_app SET is_hidden_dynamic_analysis_task = NOT(is_hidden_dynamic_analysis_task)'
        ' WHERE id = ?',
        (app_id,)
    )
    db.commit()

    return True