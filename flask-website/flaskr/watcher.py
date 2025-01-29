from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort

from flaskr.vm import get_config, get_configs, get_configs_vm_completed, new_config, get_vm_step, get_vm_error, get_vm_event, get_vm_info, get_proxmox, list_bridges, list_nodes, list_storages, create_vm, force_start_vm, force_reset_vm, delete_vm
from flaskr.auth import login_required, is_logged_in
from flaskr.db import get_db
from flaskr.apk import list_uploaded_apps, list_visible_uploaded_apps, get_app_details, save_uploaded_app, soft_delete_uploaded_app, toggle_hide_uploaded_app
from flaskr.analysis import new_task, rollback_new_task, get_task, add_to_queue, list_task, force_stop_analysis, run_adb_shell_analysis, clear_queue_del_unfinished
from proxmoxer import ProxmoxAPI, AuthenticationError
from requests import ConnectTimeout

bp = Blueprint('watcher', __name__)

@bp.route('/', methods=('GET',))
def index():
    # check auth
    if is_logged_in():
        # user logged in, redirect to main menu
        return redirect(url_for('watcher.main_menu'))

    # show main page
    return render_template('watcher/index.html')

@bp.route('/main-menu',methods=('GET',))
@login_required
def main_menu():
    return render_template('watcher/menu/base.html')

@bp.route('/android-app', methods=('GET','POST'))
@login_required
def manage_android_apps():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded', 'warning')

        app_file = request.files['file']
        if app_file.filename == '':
            flash('No file uploaded', 'warning')

        save_status = save_uploaded_app(request.files['file'])
        if not save_status:
            flash('Cannot process the uploaded file. Kindly check if it\'s a valid android application file.', 'error')

        return redirect(url_for('watcher.manage_android_apps'))

    uploaded_apps = list_uploaded_apps()
    return render_template('watcher/manage_android_app/base.html', uploaded_apps=uploaded_apps)

@bp.route('/android-app/<int:app_id>', methods=('GET','POST'))
@login_required
def manage_android_app(app_id):
    app = get_app_details(app_id=app_id)
    if app is None:
        flash(f'App with id {app_id} not found.', 'warning')
        return redirect(url_for('watcher.manage_android_apps'))

    if request.method == 'POST':
        action =  request.form['action']
        if action == 'delete':
            flash(f"App {app['package_name']}, app name {app['app_name']} is deleted.", 'info')
            soft_delete_uploaded_app(app_id=app_id)
            return redirect(url_for('watcher.manage_android_apps'))

        elif action == 'hide':
            print(app['is_hidden_dynamic_analysis_task'])
            if app['is_hidden_dynamic_analysis_task']:
                flash(f"App {app['package_name']}, app name {app['app_name']} is now shown in dynamic analysis task option.", 'info')
            else:
                flash(f"App {app['package_name']}, app name {app['app_name']} is now hidden in dynamic analysis task option.", 'info')

            toggle_hide_uploaded_app(app_id=app_id)
        else:
            flash('Invalid action', 'warning')

        return redirect(url_for('watcher.manage_android_app', app_id=app_id))

    return render_template('watcher/manage_android_app/app_details.html', app=app)

@bp.route('/dynamic-analysis-task', methods=('GET',))
@login_required
def manage_dynamic_analysis_task():
    """
    Can only see from there, task cannot be deleted, can create more
    """

    dynamic_analysis_tasks = list_task()
    return render_template('watcher/dynamic_analysis_task/details.html', dynamic_analysis_tasks=dynamic_analysis_tasks)

@bp.route('/dynamic-analysis-task/new', methods=('GET','POST'))
@login_required
def new_dynamic_analysis_task():
    configs = get_configs_vm_completed()
    if len(configs) <= 0:
        flash("You don't have any VM available and ready for dynamic analysis.")
        return redirect(url_for('watcher.main_menu'))

    if request.method == 'POST':
        install_packages = request.form.getlist('install_packages[]')
        if len(install_packages) <= 0:
            flash('Please select the packages that needs to be installed on android dynamic analysis VM.', 'warning')
            return redirect(url_for('watcher.new_dynamic_analysis_task'))

        config = request.form['config']
        sdk_level = request.form['sdk_level']
        session_duration = request.form['session_duration']
        watch_packages = request.form['watch_packages'].strip()
        run_package = request.form['run_package'].strip()
        is_manual_control = request.form.get('is_manual_control', False)
        if is_manual_control == 'on':
            is_manual_control = True
        no_internet = request.form.get('no_internet', False)
        if no_internet == 'on':
            no_internet = True

        dynamic_analysis_task_id = new_task(
            config_id=config,
            sdk_level=sdk_level,
            install_packages=install_packages,
            session_duration=session_duration,
            watch_packages=watch_packages,
            run_package=run_package,
            is_manual_control=is_manual_control,
            no_internet=no_internet,
        )

        if isinstance(dynamic_analysis_task_id, int):
            add_to_queue(dynamic_analysis_task_id=dynamic_analysis_task_id, config_id=config)
            return redirect(url_for('watcher.view_dynamic_analysis_task', task_id=dynamic_analysis_task_id))

        rollback_new_task(task_id=dynamic_analysis_task_id)
        flash('Failed to create new dynamic analysis task.', 'error')

    available_apps = list_visible_uploaded_apps()
    return render_template('watcher/dynamic_analysis_task/new.html', available_apps=available_apps, configs=configs)

@bp.route('/dynamic-analysis-task/run_cmd/<int:task_id>', methods=('POST',))
@login_required
def run_adb_shell_dynamic_analysis_task(task_id):
    """
    This route is changed from return page thingy to javascript form submission
    """
    task = get_task(task_id=task_id)
    if task is None:
        abort(404)

    analysis_adb_shell_cmd = request.form['analysis-adb-shell-cmd']

    run_adb_shell_analysis(
        task_id=task['id'],
        analysis_adb_shell_cmd=analysis_adb_shell_cmd
    )

    return jsonify({'status': 'ok'}), 200

@bp.route('/dynamic-analysis-task/clear_dangling', methods=('POST',))
@login_required
def clear_queue_del_unfinished_dynamic_analysis_task():
    clear_queue_del_unfinished.delay()

    flash(f"Queue will be cleared, VM lock will be released, dangling task will be deleted. See lock release on <a href='{url_for('watcher.vm_menu')}'>VM menu</a>.", "info")
    return redirect(url_for('watcher.manage_dynamic_analysis_task'))

@bp.route('/dynamic-analysis-task/stop/<int:task_id>', methods=('POST',))
@login_required
def stop_dynamic_analysis_task(task_id):
    task = get_task(task_id=task_id)
    if task is None:
        abort(404)

    force_stop_analysis(task_id=task['id'])

    flash(f"Dynamic analysis task #{task_id} is stopping.", "info")
    return redirect(url_for('watcher.view_dynamic_analysis_task', task_id=task_id))

@bp.route('/dynamic-analysis-task/<int:task_id>', methods=('GET','POST'))
@login_required
def view_dynamic_analysis_task(task_id):
    dynamic_analysis_task, dynamic_analysis_app, queue_dynamic_analysis_task, config = get_task(task_id=task_id, populate=True)
    if dynamic_analysis_task is None:
        abort(404)

    return render_template(
        'watcher/dynamic_analysis_task/run.html',
        dynamic_analysis_task=dynamic_analysis_task,
        dynamic_analysis_app=dynamic_analysis_app,
        queue_dynamic_analysis_task=queue_dynamic_analysis_task,
        config=config
    )

@bp.route('/vm', methods=('GET','POST'))
@login_required
def vm_menu():
    vms = get_configs()
    return render_template('watcher/vm/menu.html', vms=vms)

@bp.route('/vm/new', methods=('GET','POST'))
@login_required
def vm_new():
    def update_to_previous_step(step, id=1):
        db = get_db()
        db.execute(
            'UPDATE config SET step = ?'
            ' WHERE id = ?',
            (step - 1, id)
        )
        db.commit()

    config_id = request.args.get('config_id', None)

    if request.method == 'GET':

        if config_id is None:
            return render_template('watcher/vm/new/1_setup_proxmox_account.html', config_id=config_id)

        config = get_config(config_id)
        if config is None:
            flash('No config id', 'error')
            return redirect(url_for('watcher.vm_new'))

        if config['step'] == 1:
            return render_template('watcher/vm/new/1_setup_proxmox_account.html', config_id=config_id)
        if config['step'] == 2:
            # pass proxmox nodes data
            nodes = list_nodes(config_id)

            if nodes is None:
                flash('Cannot get node list from Proxmox VE. Please check if configuration is valid.', 'error')
                update_to_previous_step(config['step'], config_id)
                return redirect(url_for('watcher.vm_new', config_id=config_id))

            nodes.sort()
            return render_template('watcher/vm/new/2_select_proxmox_node.html', nodes=nodes, config_id=config_id)
        elif config['step'] == 3:
            # pass proxmox storage data
            storages = list_storages(config_id)

            if storages is None:
                flash('Cannot get storage list from Proxmox VE. Please check if configuration is valid.', 'error')
                update_to_previous_step(config['step'], config_id)
                return redirect(url_for('watcher.vm_new', config_id=config_id))
            
            storages.sort()
            return render_template('watcher/vm/new/3_select_storage.html', storages=storages, config_id=config_id)
        elif config['step'] == 4:
            bridges = list_bridges(config_id)

            if bridges is None:
                flash('Cannot get bridge list from Proxmox VE. Please check if configuration is valid.', 'error')
                update_to_previous_step(config['step'] - 1, config_id)
                return redirect(url_for('watcher.vm_new', config_id=config_id))

            bridges.sort()
            return render_template('watcher/vm/new/4_select_bridge.html', bridges=bridges, config_id=config_id)
        elif config['step'] == 5:
            # pass proxmox vm deploy data logic
            # vm_step and error variable
            vm_step = get_vm_step(config_id)
            error = get_vm_error(config_id)
            event = get_vm_event(config_id)
            vm = get_vm_info(config_id)

            if vm_step < 0 or vm_step >= 5:
                step = 6 if vm_step >= 5 else 5
                db = get_db()
                db.execute(
                    'UPDATE config SET step = ?'
                    ' WHERE id = ?',
                    (step, config_id)
                )
                db.commit()

            return render_template('watcher/vm/new/5_deploy_android_analysis_vm.html', vm_step=vm_step, vm=vm, error=error, event=event, config_id=config_id)
        elif config['step'] == 6:
            # first setup finished
            return redirect(url_for('watcher.vm_menu'))

    if request.method == 'POST':

        setup_step = int(request.form['step'])
        setup_action = request.form['action']

        config = get_config(config_id)
        if setup_step != 1 and config_id is None:
            flash('No config id', 'error')
            return redirect(url_for('watcher.vm_new'))

        if setup_step == 1:
            if config_id is None:
                config_id = new_config()

            proxmox_host_address = request.form['host_address']
            proxmox_account_realm = request.form['realm']
            proxmox_account_username = request.form['username']
            proxmox_account_password = request.form['password']
            proxmox_vm_core = request.form['core']
            proxmox_vm_memory = request.form['memory']
            proxmox_vm_disk = request.form['disk']

            prox = get_proxmox(
                config_id,
                proxmox_host_address,
                proxmox_account_realm,
                proxmox_account_username,
                proxmox_account_password,
                5
            )

            if prox is None:
                flash('Cannot connect to Proxmox VE. Please check if all value is valid.', 'error')
                return redirect(url_for('watcher.vm_new', config_id=config_id))
            
            if not isinstance(prox, ProxmoxAPI):
                if isinstance(prox, AuthenticationError):
                    flash('Cannot login to Proxmox VE. Please check if the provided value is valid.', 'error')
                elif isinstance(prox, ConnectTimeout):
                    flash('Connection timeout while connecting to Proxmox VE. Please check if all value is valid and this website\'s host can access the Proxmox VE.')
                else:
                    flash('Cannot connect to Proxmox VE. Please check if all value is valid.')
                return redirect(url_for('watcher.vm_new', config_id=config_id))

            db = get_db()
            db.execute(
                'REPLACE INTO'
                ' config (is_deleted_from_proxmox, id, step, proxmox_host_address, proxmox_account_realm, proxmox_account_username, proxmox_account_password, proxmox_vm_android_analysis_memory, proxmox_vm_android_analysis_core, proxmox_vm_android_analysis_disk)'
                ' VALUES (0, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (config_id, setup_step + 1, proxmox_host_address, proxmox_account_realm, proxmox_account_username, proxmox_account_password, proxmox_vm_memory, proxmox_vm_core, proxmox_vm_disk)
            )
            db.commit()
            return redirect(url_for('watcher.vm_new', config_id=config_id))
        elif setup_step == 2:
            if setup_action == 'previous':
                db = get_db()
                db.execute(
                    'UPDATE config SET step = ?'
                    ' WHERE id = ?',
                    (setup_step - 1, config_id)
                )
                db.commit()
                return redirect(url_for('watcher.vm_new', config_id=config_id))

            node = request.form['node']
            db = get_db()
            db.execute(
                'UPDATE config SET step = ?, proxmox_node = ?'
                ' WHERE id = ?',
                (setup_step + 1, node, config_id)
            )
            db.commit()
            return redirect(url_for('watcher.vm_new', config_id=config_id))
        elif setup_step == 3:
            if setup_action == 'previous':
                db = get_db()
                db.execute(
                    'UPDATE config SET step = ?'
                    ' WHERE id = ?',
                    (setup_step - 1, config_id)
                )
                db.commit()
                return redirect(url_for('watcher.vm_new', config_id=config_id))
            storage = request.form['storage']
            db = get_db()
            db.execute(
                'UPDATE config SET step = ?, proxmox_storage = ?'
                ' WHERE id = ?',
                (setup_step + 1, storage, config_id)
            )
            db.commit()
            return redirect(url_for('watcher.vm_new', config_id=config_id))
        elif setup_step == 4:
            if setup_action == 'previous':
                db = get_db()
                db.execute(
                    'UPDATE config SET step = ?'
                    ' WHERE id = ?',
                    (setup_step - 1, config_id)
                )
                db.commit()
                return redirect(url_for('watcher.vm_new', config_id=config_id))
            bridge = request.form['bridge']
            db = get_db()
            db.execute(
                'UPDATE config SET step = ?, proxmox_bridge = ?, vm_step = ?'
                ' WHERE id = ?',
                (setup_step + 1, bridge, 1, config_id)
            )
            db.commit()

            result = create_vm.delay(
                config_id, 'watcher-android-vm'
            )

            return redirect(url_for('watcher.vm_new', config_id=config_id))
        elif setup_step == 5:
            db = get_db()
            db.execute(
                'UPDATE config SET step = ?'
                ' WHERE id = ?',
                (setup_step + 1, config_id)
            )
            db.commit()
            return redirect(url_for('watcher.vm_new', config_id=config_id))

    return redirect(url_for('watcher.vm_menu'))

@bp.route('/vm/<int:config_id>', methods=('GET',))
@login_required
def vm_details(config_id):
    config = get_config(config_id)

    if config is None:
        flash("VM does not exists.", "warn")
        return redirect(url_for('watcher.vm_menu'))

    if config['step'] < 5 or config['vm_step'] < 5:
        flash("VM is in creation.", "info")
        return redirect(url_for('watcher.vm_new', config_id=config_id))

    # pass proxmox vm deploy data logic
    # vm_step and error variable
    error = get_vm_error(config_id)
    event = get_vm_event(config_id)
    vm = get_config(config_id)

    return render_template('watcher/vm/details.html', vm=vm, error=error, event=event, config_id=config_id)

@bp.route('/vm/start/<int:config_id>', methods=('POST',))
@login_required
def vm_force_start(config_id):
    config = get_config(config_id)
    if config is None:
        flash("VM does not exists.", "warn")
        return redirect(url_for('watcher.vm_menu'))

    if config['step'] < 5:
        flash("VM is in creation.", "info")
        return redirect(url_for('watcher.vm_new', config_id=config_id))

    flash("VM will be started if it's currently down. IP address should be gone and back in a minute", "info")
    force_start_vm.delay(config_id)
    return redirect(url_for('watcher.vm_details', config_id=config_id))

@bp.route('/vm/reset/<int:config_id>', methods=('POST',))
@login_required
def vm_force_reset(config_id):
    config = get_config(config_id)
    if config is None:
        flash("VM does not exists.", "warn")
        return redirect(url_for('watcher.vm_menu'))

    if config['step'] < 5:
        flash("VM is in creation.", "info")
        return redirect(url_for('watcher.vm_new', config_id=config_id))

    flash("VM will be reset. IP address should be gone and back in a minute", "info")
    force_reset_vm.delay(config_id)
    return redirect(url_for('watcher.vm_details', config_id=config_id))

@bp.route('/vm/delete/<int:config_id>', methods=('POST',))
@login_required
def vm_force_delete(config_id):
    config = get_config(config_id)
    if config is None:
        flash("VM does not exists.", "warn")
        return redirect(url_for('watcher.vm_menu'))

    if config['step'] < 5:
        flash("Someone is still filling the VM creation form.", "info")
        return redirect(url_for('watcher.vm_new', config_id=config_id))

    delete_vm.delay(config_id)
    flash(f"VM #{config_id} with VMID {config['proxmox_vm_android_analysis_id']} is being deleted.", "info")
    return redirect(url_for('watcher.main_menu'))
