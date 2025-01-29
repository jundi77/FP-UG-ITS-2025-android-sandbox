from celery import shared_task
from flask import current_app, g
from flaskr.db import get_db
from flaskr.vm import get_config, get_configs
from flaskr.utils.ansible import run_ansible_new_analysis, run_ansible_stop_analysis, log_new_analysis_error_to_db, run_ansible_run_adb_shell_analysis
import os, time, random, string, requests, datetime, json

runner_worker = {}

"""
Save to websockify token file in the instance directory
"""
def add_websockify_cfg(id, data, websockify_token_path):
    with open(os.path.join(websockify_token_path, str(id)), 'w') as f:
        f.write(f"{id}: {data}\n")

"""
Remove related file in the websockify config
"""
def remove_websockify_cfg(id, websockify_token_path):
    try:
        os.remove(os.path.join(websockify_token_path, str(id)))
    except:
        # Whatever, just means the file isn't there :D
        return

def get_task(task_id, populate=False):
    db = get_db()
    task = db.execute(
        'SELECT * FROM dynamic_analysis_task WHERE id = ?', (task_id,)
    ).fetchone()

    if populate == True:
        if task is not None:
            config = get_config(task['config_id'])
            task_installed_app = db.execute(
                'SELECT * FROM dynamic_analysis_app dap'
                ' INNER JOIN android_app aa ON dap.android_app_id = aa.id'
                ' WHERE dap.dynamic_analysis_task_id = ?', (task_id,)
            ).fetchall()

            task_queue = db.execute(
                'SELECT COUNT(*) AS count'
                ' FROM queue_dynamic_analysis_task qat'
                ' INNER JOIN dynamic_analysis_task dat'
                ' ON qat.dynamic_analysis_task_id=dat.id'
                ' WHERE qat.dynamic_analysis_task_id < ?'
                ' AND dat.config_id = ?',
                (task_id,config['id'])
            ).fetchone()
        else:
            config = None
            task_installed_app = None
            task_queue = None

        return (task, task_installed_app, task_queue, config)
    
    return task

def is_task_done(task_id):
    db = get_db()
    task = db.execute(
        'SELECT end_session FROM dynamic_analysis_task WHERE id = ?', (task_id,)
    ).fetchone()

    if task is None:
        return True # IT DOES NOT EXISTS! Cry about it.

    return task['end_session'] is not None

def rollback_new_task(task_id):
    """
    No queue added for this task, so... yeah. Don't care. Hehe.
    """
    db = get_db()

    db.execute(
        'DELETE FROM dynamic_analysis_app WHERE dynamic_analysis_task_id = ?',
        (task_id,)
    )

    db.execute(
        'DELETE FROM dynamic_analysis_task WHERE id = ?',
        (task_id,)
    )
    db.commit()

@shared_task
def clear_queue_del_unfinished():
    """
    No matter what, release lock on VM.
    """
    db = get_db()

    unfinished_tasks = db.execute(
        'SELECT id FROM dynamic_analysis_task WHERE end_session IS NULL'
    ).fetchall()

    for unfinished_task in unfinished_tasks:
        force_stop_analysis(unfinished_task['id'])
        queue_analysis_stopper_worker(unfinished_task['id'])
        db.execute(
            'DELETE FROM dynamic_analysis_task WHERE id = ?', (unfinished_task['id'],)
        )
        db.commit()

    db.execute('DELETE FROM queue_dynamic_analysis_task')
    db.commit()

    configs = get_configs()
    for config in configs:
        vm_address = config['proxmox_vm_android_analysis_ip']
        vm_username = 'ubuntu'
        vm_password = 'UbuntuWatcher'

        result = False
        count = 1
        while result != True and count < 10:
            # attempt to stop any dangling task in the vm
            result = run_ansible_stop_analysis(
                app_abs_path=os.path.abspath(
                    os.path.dirname(current_app.instance_path)
                ),
                host_address=vm_address,
                username=vm_username,
                password=vm_password
            )

            if result != True:
                count += 1
                time.sleep(1)

        # release lock vm resource, no matter what
        db.execute(
            'UPDATE config SET lock_dynamic_analysis_task_id = ?'
            ' WHERE id = ?',
            (None, config['id'],)
        )
        db.commit()

def new_task(config_id, sdk_level, install_packages, session_duration, watch_packages, run_package, is_manual_control, no_internet):
    user_id = g.user['id']

    db = get_db()
    task = db.execute(
        'INSERT INTO dynamic_analysis_task (config_id, user_id, sdk_level, watch_packages, run_package, is_manual_control, no_internet, session_duration, vnc_password)'
        ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (config_id, user_id, sdk_level, watch_packages, run_package, is_manual_control, no_internet, session_duration, ''.join(random.choices(string.ascii_letters, k=9)))
    )
    db.commit()

    for package_id in install_packages:
        db.execute(
            'INSERT INTO dynamic_analysis_app (dynamic_analysis_task_id, android_app_id)'
            ' VALUES (?, ?)',
            (task.lastrowid, package_id)
        )
        db.commit()

    return task.lastrowid

def list_task():
    db = get_db()
    tasks = db.execute(
        'SELECT * FROM dynamic_analysis_task WHERE user_id = ? ORDER BY id DESC', (g.user['id'],)
    ).fetchall()

    return tasks

def add_to_queue(dynamic_analysis_task_id, config_id):
    db = get_db()
    db.execute(
        'INSERT INTO queue_dynamic_analysis_task (dynamic_analysis_task_id) VALUES (?)',
        (dynamic_analysis_task_id,)
    )
    db.commit()

    if runner_worker.get(dynamic_analysis_task_id, None) is not None:
        return False

    runner_worker[dynamic_analysis_task_id] = queue_analysis_runner_worker.delay(dynamic_analysis_task_id, config_id)
    return True

def add_log_to_task(dynamic_analysis_task_id, log_type, log_action, log_msg, log_data, log_timestamp):
    db = get_db()
    db.execute(
        'INSERT INTO dynamic_analysis_log'
        ' (dynamic_analysis_task_id, log_type, log_action, log_msg, log_data, log_timestamp)'
        ' VALUES'
        ' (?, ?, ?, ?, ?, ?)',
        (dynamic_analysis_task_id, log_type, log_action, log_msg, log_data, log_timestamp)
    )
    db.commit()

@shared_task
def queue_analysis_runner_worker(dynamic_analysis_task_id, config_id):
    db = get_db()
    app_path = os.path.dirname(current_app.instance_path)

    while True:
        # get queue, only continue if we are the chosen one on queue
        queue_id = db.execute(
            'SELECT dynamic_analysis_task_id FROM queue_dynamic_analysis_task qat'
            ' ORDER BY qat.id DESC'
            ' LIMIT 1'
        ).fetchone()

        if queue_id is None:
            return False

        if queue_id['dynamic_analysis_task_id'] == dynamic_analysis_task_id:
            # We are the chosen one, continue
            break

        time.sleep(10)

    while True:
        # check vm if used (lock)
        queue = db.execute(
            'SELECT * FROM queue_dynamic_analysis_task qat'
            ' INNER JOIN dynamic_analysis_task dat ON dat.id=qat.dynamic_analysis_task_id'
            ' INNER JOIN config c ON c.id=dat.config_id'
            ' WHERE dat.config_id = ?'
            ' AND qat.dynamic_analysis_task_id = ?'
            ' ORDER BY qat.id DESC'
            ' LIMIT 1',
            (config_id,dynamic_analysis_task_id)
        ).fetchone()

        if queue is None:
            return False

        if queue['lock_dynamic_analysis_task_id'] is None:
            break

        time.sleep(5)

    task_id = queue['dynamic_analysis_task_id']

    # try to lock vm resource for this analysis
    db.execute(
        'UPDATE config SET lock_dynamic_analysis_task_id = ?'
        ' WHERE id = ?',
        (task_id, config_id,)
    )
    db.commit()

    ##### VM IS LOCKED FOR THIS TASK #####

    # run dynamic analysis
    vm_address = queue['proxmox_vm_android_analysis_ip']
    vm_username = 'ubuntu'
    vm_password = 'UbuntuWatcher'

    analysis_sdk_level = queue['sdk_level']
    analysis_watch_packages = queue['watch_packages']
    analysis_run_package = queue['run_package']
    analysis_is_manual_control = queue['is_manual_control']
    analysis_no_internet = queue['no_internet']
    analysis_session_duration = queue['session_duration']
    analysis_vnc_password = queue['vnc_password']
    analysis_install_apps = db.execute(
        'SELECT * FROM dynamic_analysis_app dap'
        ' INNER JOIN dynamic_analysis_task dat ON dat.id=dap.dynamic_analysis_task_id'
        ' INNER JOIN android_app aa ON aa.id=dap.android_app_id'
        ' WHERE dap.dynamic_analysis_task_id = ?',
        (task_id,)
    ).fetchall()

    analysis_install_files = [
        {
            'src': os.path.abspath(os.path.join(current_app.config['UPLOAD_FOLDER'], app['filename'])),
            'filename': app['filename']
        } for app in analysis_install_apps
    ]

    extravars = {
        'vnc_password': analysis_vnc_password,
        'analysis_sdk_level': analysis_sdk_level,
        'android_app_files': analysis_install_files,
        'analysis_watch_packages': analysis_watch_packages,
        'analysis_run_package': analysis_run_package,
        'analysis_is_manual_control': analysis_is_manual_control,
        'analysis_no_internet': analysis_no_internet,
        'task_id': task_id,
    }

    result = False
    count = 1
    while result != True and count < 10:
        result = run_ansible_new_analysis(
            db=db,
            task_id=task_id,
            app_abs_path=os.path.abspath(app_path),
            host_address=vm_address,
            username=vm_username,
            password=vm_password,
            extravars=extravars
        )
        if result != True:
            count += 1
            time.sleep(1)

    db.execute(
        'UPDATE dynamic_analysis_task SET start_session = CURRENT_TIMESTAMP WHERE id = ?',
        (task_id,)
    )
    db.commit()

    if result != True:
        # end prematurely
        log_new_analysis_error_to_db(db, task_id, f"Start dynamic analysis from ansible failed: {result}.")
        db.execute(
            'UPDATE dynamic_analysis_task SET end_session = CURRENT_TIMESTAMP WHERE id = ?',
            (task_id,)
        )
        db.commit()

        queue_analysis_stopper_worker(task_id)

        return False

    add_websockify_cfg(
        task_id,
        f'{vm_address}:5901',
        os.path.abspath(current_app.config['WEBSOCKIFY_TOKEN_FOLDER'])
    )

    duration = analysis_session_duration * 60 # because it is saved in minutes
    start_time = time.time()
    config = get_config(config_id)
    url = f'http://{config["proxmox_vm_android_analysis_ip"]}:9999/api/android_watcher_log'

    while True:
        time.sleep(1)
        elapsed_time = time.time() - start_time
        if elapsed_time > duration or is_task_done(task_id=dynamic_analysis_task_id):
            break

        try:
            response = requests.get(url=url)
        except Exception:
            # meh, don't care
            continue

        print(response.json())
        if response.status_code == 200:
            """
            response will look like this, if there is log on queue:
            {
                id: <task_id>,
                timestamp: <timestamp in miliseconds>,
                type: <type>,
                action: <action>,
                msg: <msg>,
                data: {
                    ...<extended data>
                }
            }
            """
            data = response.json()
            data_task_id = data.get('id', '')
            if task_id != data_task_id:
                continue

            data_timestamp = data.get('timestamp', None)
            if data_timestamp is None:
                continue
            data_timestamp = datetime.datetime.fromtimestamp(data_timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S.%f')[:-2] #SS.SSS format

            data_type = data.get('type', None)
            if data_type is None:
                continue

            data_action = data.get('action', None)
            if data_action is None:
                continue

            data_msg = data.get('msg', None)
            if data_msg is None:
                continue

            data_additional_data = data.get('data', None)
            if data_additional_data is not None:
                # this is specific to each action, let the user decide for themself
                data_additional_data = json.dumps(data_additional_data)
            
            add_log_to_task(
                dynamic_analysis_task_id=task_id,
                log_timestamp=data_timestamp,
                log_type=data_type,
                log_action=data_action,
                log_msg=data_msg,
                log_data=data_additional_data
            )

    # dynamic analysis stopper when exceeding duration
    queue_analysis_stopper_worker(task_id)

def force_stop_analysis(task_id):
    # Need to put end_session and the loop get log thingy on queue_analysis_runner_worker will exit
    # then it continues and run stop procedure

    db = get_db()
    db.execute(
        'UPDATE dynamic_analysis_task SET end_session = CURRENT_TIMESTAMP WHERE id = ?',
        (task_id,)
    )
    db.commit()


    # There will be double update on end_session, first as the stop flag above,
    # second as final end_session time by queue_analysis_stopper_worker.
    queue_analysis_stopper_worker.delay(task_id)

@shared_task
def run_adb_shell_analysis(task_id, analysis_adb_shell_cmd):
    db = get_db()

    # get queue
    queue = db.execute(
        'SELECT * FROM queue_dynamic_analysis_task qat'
        ' INNER JOIN dynamic_analysis_task dat ON dat.id=qat.dynamic_analysis_task_id'
        ' INNER JOIN config c ON c.id=dat.config_id'
        ' WHERE dynamic_analysis_task_id = ?'
        ' AND end_session IS NULL'
        ' ORDER BY qat.id DESC'
        ' LIMIT 1',
        (task_id,)
    ).fetchone()

    if queue is None:
        return # somehow have stopped or cleared from queue idk

    app_path = os.path.dirname(current_app.instance_path)

    # get dynamic analysis data
    vm_address = queue['proxmox_vm_android_analysis_ip']
    vm_username = 'ubuntu'
    vm_password = 'UbuntuWatcher'

    result = False
    count = 1
    while result != True and count < 10:
        result = run_ansible_run_adb_shell_analysis(
            app_abs_path=os.path.abspath(app_path),
            host_address=vm_address,
            username=vm_username,
            password=vm_password,
            extravars={
                'analysis_adb_shell_cmd': analysis_adb_shell_cmd
            }
        )
        if result != True:
            count += 1
            time.sleep(1)

    if result != True:
        # end prematurely
        return False

    return True

@shared_task
def queue_analysis_stopper_worker(task_id):
    remove_websockify_cfg(task_id, os.path.abspath(current_app.config['WEBSOCKIFY_TOKEN_FOLDER']))

    db = get_db()

    """
    I'm sorry, what? end_session is set? by who?
    Only I. Can. Set. end_session.
    B E G O N E.
    """
    queue = db.execute(
        'SELECT * FROM queue_dynamic_analysis_task qat'
        ' LEFT JOIN dynamic_analysis_task dat ON dat.id=qat.dynamic_analysis_task_id'
        ' LEFT JOIN config c ON c.id=dat.config_id'
        ' WHERE qat.dynamic_analysis_task_id = ?'
        ' ORDER BY qat.id DESC'
        ' LIMIT 1',
        (task_id,)
    ).fetchone()

    if queue is None:
        return # somehow have stopped or cleared from queue idk

    config_id = queue['config_id']
    app_path = os.path.dirname(current_app.instance_path)

    if queue['lock_dynamic_analysis_task_id'] == task_id:
        """
        only stop the current running task if the task is the one who lock
        ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⠿⠿⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
        ⣿⣿⣿⣿⣿⣿⣿⣿⠟⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠉⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
        ⣿⣿⣿⣿⣿⣿⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢺⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
        ⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠆⠜⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
        ⣿⣿⣿⣿⠿⠿⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠻⣿⣿⣿⣿⣿
        ⣿⣿⡏⠁⠀⠀⠀⠀⠀⣀⣠⣤⣤⣶⣶⣶⣶⣶⣦⣤⡄⠀⠀⠀⠀⢀⣴⣿⣿⣿⣿⣿
        ⣿⣿⣷⣄⠀⠀⠀⢠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢿⡧⠇⢀⣤⣶⣿⣿⣿⣿⣿⣿⣿
        ⣿⣿⣿⣿⣿⣿⣾⣮⣭⣿⡻⣽⣒⠀⣤⣜⣭⠐⢐⣒⠢⢰⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿
        ⣿⣿⣿⣿⣿⣿⣿⣏⣿⣿⣿⣿⣿⣿⡟⣾⣿⠂⢈⢿⣷⣞⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿
        ⣿⣿⣿⣿⣿⣿⣿⣿⣽⣿⣿⣷⣶⣾⡿⠿⣿⠗⠈⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
        ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠻⠋⠉⠑⠀⠀⢘⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
        ⣿⣿⣿⣿⣿⣿⣿⡿⠟⢹⣿⣿⡇⢀⣶⣶⠴⠶⠀⠀⢽⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
        ⣿⣿⣿⣿⣿⣿⡿⠀⠀⢸⣿⣿⠀⠀⠣⠀⠀⠀⠀⠀⡟⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
        ⣿⣿⣿⡿⠟⠋⠀⠀⠀⠀⠹⣿⣧⣀⠀⠀⠀⠀⡀⣴⠁⢘⡙⢿⣿⣿⣿⣿⣿⣿⣿⣿
        ⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⢿⠗⠂⠄⠀⣴⡟⠀⠀⡃⠀⠉⠉⠟⡿⣿⣿⣿⣿
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢷⠾⠛⠂⢹⠀⠀⠀⢡⠀⠀⠀⠀⠀⠙⠛⠿⢿
        """

        vm_address = queue['proxmox_vm_android_analysis_ip']
        vm_username = 'ubuntu'
        vm_password = 'UbuntuWatcher'

        result = False
        count = 1
        while result != True and count < 10:
            # attempt to stop task
            result = run_ansible_stop_analysis(
                app_abs_path=os.path.abspath(app_path),
                host_address=vm_address,
                username=vm_username,
                password=vm_password
            )

            if result != True:
                count += 1
                time.sleep(1)

        """
        release lock vm resource for this analysis.
        ignoring if attempt to stop the task is succesfull, because it's
        very important that the lock is released so that resource can be used
        by other task rather than being concerned about this task.
        """
        db.execute(
            'UPDATE config SET lock_dynamic_analysis_task_id = ?'
            ' WHERE id = ?',
            (None, config_id,)
        )

    db.execute(
        'UPDATE dynamic_analysis_task SET end_session = CURRENT_TIMESTAMP WHERE id = ?',
        (task_id,)
    )

    db.execute(
        'DELETE FROM queue_dynamic_analysis_task'
        ' WHERE id = ?',
        (queue['id'],)
    )

    db.commit()
