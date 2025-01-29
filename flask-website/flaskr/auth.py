import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

def is_logged_in():
    return g.user is not None

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)

    return wrapped_view

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            "SELECT * FROM user WHERE id = ?", (user_id,)
        ).fetchone()

def register_user(username, password):
    db = get_db()
    try:
        db.execute(
            "INSERT INTO user (username, password) VALUES (?, ?)",
            (username, generate_password_hash(password))
        )
        db.commit()
    except db.IntegrityError:
        return f'User {username} is already registered.'

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username required.'
        elif not password:
            error = 'Password required'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password))
                )
                db.commit()
            except db.IntegrityError:
                error = f'User {username} is already registered.'
            else:
                return redirect(url_for('auth.login'))

        flash(error, 'error')

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error, 'error')

    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@bp.route('/change-pass', methods=('GET', 'POST'))
@login_required
def change_pass():
    if request.method == 'POST':
        new_password = request.form['new-password']
        confirm_new_password = request.form['confirm-new-password']

        if new_password != confirm_new_password:
            flash('New password and confirm password is different.', 'warn')
            return redirect(url_for('auth.change_pass'))

        db = get_db()
        error = None

        user = db.execute(
            'SELECT * FROM user WHERE id = ?', (g.user['id'],)
        ).fetchone()

        if user is None:
            error = 'No user.'
            flash(error, 'error')
            return redirect(url_for('watcher.main_menu'))

        db.execute(
            "UPDATE user SET password = ? WHERE id = ?",
            (generate_password_hash(new_password), g.user['id'])
        )
        db.commit()
        flash('Password changed.', 'info')

    return render_template('auth/change-pass.html')
