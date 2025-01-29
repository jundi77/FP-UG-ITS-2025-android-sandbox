from flask import (
    Blueprint, request,jsonify,
)
from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('api', __name__)

def get_logs(task_id, log_last_id=None):
    if log_last_id is None or log_last_id == 0:
        logs = get_db().execute(
            'SELECT * FROM dynamic_analysis_log'
            ' WHERE dynamic_analysis_task_id = ?'
            ' ORDER BY id',
            (task_id,)
        ).fetchall()
    else:
        logs = get_db().execute(
            'SELECT * FROM dynamic_analysis_log'
            ' WHERE dynamic_analysis_task_id = ? AND id > ?'
            ' ORDER BY id',
            (task_id, log_last_id)
        ).fetchall()

    logs = [dict(log) for log in logs]
    return logs

@bp.route('/api/logs/<int:task_id>', methods=('GET','POST'))
@login_required
def get_logs_api(task_id):
    db = get_db()
    task = db.execute(
        'SELECT id, end_session FROM dynamic_analysis_task WHERE id = ?', (task_id,)
    ).fetchone()

    if task is None:
        return jsonify({
            'error': 'No task with provided id.'
        }), 404

    response = {
        'data': get_logs(
            task['id'],
            request.args.get('last_id', None),
        )
    }

    if task['end_session'] is not None:
        response['stop_live_log'] = True

    return jsonify(response), 200