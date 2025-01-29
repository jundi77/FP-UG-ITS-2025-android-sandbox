from ansi2html import Ansi2HTMLConverter
import ansible_runner
import os

def log_new_vms_error_to_db(db, id, msg):
    db.execute(
        'UPDATE config SET error_message = ?'
        ' WHERE id = ?',
        (msg, id)
    )
    db.commit()

def log_new_vms_event_to_db(db, id, msg):
    db.execute(
        'UPDATE config SET event_message = ?'
        ' WHERE id = ?',
        (msg, id)
    )
    db.commit()

def log_new_analysis_error_to_db(db, id, msg):
    db.execute(
        'UPDATE dynamic_analysis_task SET error_message = ?'
        ' WHERE id = ?',
        (msg, id)
    )
    db.commit()

def log_new_analysis_event_to_db(db, id, msg):
    db.execute(
        'UPDATE dynamic_analysis_task SET event_message = ?'
        ' WHERE id = ?',
        (msg, id)
    )
    db.commit()

def create_inline_host_inventory(host_address, username, password):
    return f"""
    [watcher_android_analysis_vm]
    {host_address} ansible_user={username} ansible_ssh_pass={password} ansible_become_password={password} ansible_ssh_extra_args="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
    """ # ansible_python_interpreter=/usr/bin/python3 -> weird if in windows

def get_playbook_file(app_abs_path, filename):
    return os.path.join(
        app_abs_path,
        'instance-setup',
        'watcher-emulator',
        'ansible',
        filename
    )

def run_ansible_new_vms(db, config_id, app_abs_path, host_address, username, password):
    def log_ansible_event_to_db(event):
        if event.get('event', '') == 'runner_on_failed':
            logger = log_new_vms_error_to_db
        else:
            logger = log_new_vms_event_to_db

        event_msg = event.get('stdout', '')
        if event_msg == '':
            play = event['event_data'].get('play', '')
            task = event['event_data'].get('task', '')
            event_msg = f'"{play}: {task}".'
        else:
            conv = Ansi2HTMLConverter()
            event_msg = conv.convert(event_msg, full=False)

        logger(db=db, id=config_id, msg=event_msg)
        return True

    # make host inventory
    inline_inventory = create_inline_host_inventory(
        host_address=host_address,
        username=username,
        password=password
    )

    result = ansible_runner.run(
        playbook=get_playbook_file(app_abs_path, 'new-vm.yml'),
        json_mode=True,
        inventory=inline_inventory, 
        event_handler=log_ansible_event_to_db,
    )

    all_events = list(result.events)

    if result.rc == 0:
        print("Ansible playbook for new vm creation is done succesfully.")
        return True

    print("Ansible playbook for new vm creation failed.")
    return False

def run_ansible_new_analysis(db, task_id, app_abs_path, host_address, username, password, extravars):
    def log_ansible_event_to_db(event):
        if event.get('event', '') == 'runner_on_failed':
            return
            # logger = log_new_analysis_error_to_db
        else:
            logger = log_new_analysis_event_to_db

        event_msg = event.get('stdout', '')
        if event_msg == '':
            play = event['event_data'].get('play', '')
            task = event['event_data'].get('task', '')
            event_msg = f'"{play}: {task}".'
        else:
            conv = Ansi2HTMLConverter()
            event_msg = conv.convert(event_msg, full=False)

        logger(db=db, id=task_id, msg=event_msg)
        return True

    # make host inventory
    inline_inventory = create_inline_host_inventory(
        host_address=host_address,
        username=username,
        password=password
    )

    result = ansible_runner.run(
        playbook=get_playbook_file(app_abs_path, 'start-dynamic-analysis.yml'),
        json_mode=True,
        inventory=inline_inventory,
        extravars=extravars,
        event_handler=log_ansible_event_to_db,
    )

    if result.rc == 0:
        print("Ansible playbook for new dynamic analysis task is done succesfully.")
        return True
    print("Ansible playbook for new dynamic analysis task failed.")
    return False

def run_ansible_run_adb_shell_analysis(app_abs_path, host_address, username, password, extravars):
    # make host inventory
    inline_inventory = create_inline_host_inventory(
        host_address=host_address,
        username=username,
        password=password
    )

    result = ansible_runner.run(
        playbook=get_playbook_file(app_abs_path, 'run-adb-shell-command.yml'),
        inventory=inline_inventory,
        extravars=extravars,
    )

    if result.rc == 0:
        print("Ansible playbook for running adb shell is done succesfully.")
        return True

    print("Ansible playbook for running adb shell failed.")
    return False

def run_ansible_stop_analysis(app_abs_path, host_address, username, password):
    # make host inventory
    inline_inventory = create_inline_host_inventory(
        host_address=host_address,
        username=username,
        password=password
    )

    result = ansible_runner.run(
        playbook=get_playbook_file(app_abs_path, 'stop-dynamic-analysis.yml'),
        inventory=inline_inventory,
    )

    if result.rc == 0:
        print("Ansible playbook for stop dynamic analysis task is done succesfully.")
        return True

    print("Ansible playbook for stop dynamic analysis task failed.")
    return False
