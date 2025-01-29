from celery import shared_task
from flask import current_app, g
from proxmoxer import ProxmoxAPI, AuthenticationError
from requests import ConnectTimeout, ConnectionError
from flaskr.db import get_db
from flaskr.utils.ansible import run_ansible_new_vms
import os, time

def get_configs():
    return get_db().execute(
        'SELECT * FROM config WHERE is_deleted_from_proxmox != 1'
    ).fetchall()

def get_configs_vm_completed():
    return get_db().execute(
        'SELECT *, ('
            'SELECT COUNT(*)'
            ' FROM dynamic_analysis_task dat'
            ' WHERE dat.config_id=c.id'
            ' AND dat.end_session IS NULL'
        ') AS queue_count FROM config c'
        ' WHERE c.vm_step = 5 AND c.is_deleted_from_proxmox != 1 AND c.proxmox_vm_android_analysis_ip IS NOT NULL ORDER BY queue_count, c.id'
    ).fetchall()

def get_config(id):
    return get_db().execute(
        'SELECT * FROM config WHERE id = ? AND is_deleted_from_proxmox != 1', (id,)
    ).fetchone()

def new_config():
    db = get_db()
    config = db.execute(
        'INSERT INTO'
        ' config (step)'
        ' VALUES (?)',
        (1,)
    )
    db.commit()

    return config.lastrowid

def get_vm_step(id):
    return get_config(id)['vm_step']

def get_vm_error(id):
    return get_config(id)['error_message']

def get_vm_event(id):
    return get_config(id)['event_message']

def get_vm_info(id):
    config = get_config(id)

    return {
        'id': config['proxmox_vm_android_analysis_id'],
        'name': config['proxmox_vm_android_analysis_name'],
        'ip': config['proxmox_vm_android_analysis_ip'],
    }

def change_vm_step(id, step):
    db = get_db()

    db.execute(
        'UPDATE config SET vm_step = ?'
        ' WHERE id = ?',
        (step, id)
    )
    db.commit()

def log_error_to_db(id, msg):
    db = get_db()
    db.execute(
        'UPDATE config SET error_message = ?'
        ' WHERE id = ?',
        (msg, id)
    )
    db.commit()

def log_event_to_db(id, msg):
    db = get_db()
    db.execute(
        'UPDATE config SET event_message = ?'
        ' WHERE id = ?',
        (msg, id)
    )
    db.commit()

def get_proxmox(id, host_address=None, account_realm=None, account_username=None, account_password=None, timeout=240):
    config = get_config(id)
    if config is not None and (host_address is None or account_realm is None or account_username is None or account_password is None):
        # get from db
        host_address = config['proxmox_host_address']
        account_realm = config['proxmox_account_realm']
        account_username = config['proxmox_account_username']
        account_password = config['proxmox_account_password']

    try:
        return ProxmoxAPI(host=host_address, user=f'{account_username}@{account_realm}', password=account_password, verify_ssl=False, service='pve', timeout=timeout)
    except (AuthenticationError, ConnectTimeout) as e:
        return None

def list_bridges(id):
    try:
        config = get_config(id)
        prox = get_proxmox(id=id, timeout=5)

        if not isinstance(prox, ProxmoxAPI):
            return prox

        bridges = prox.nodes(config['proxmox_node']).network.get(type='bridge')
        return [bridges['iface'] for bridges in bridges]
    except:
        return None

def list_storages(id):
    try:
        config = get_config(id)
        prox = get_proxmox(id=id, timeout=5)

        if not isinstance(prox, ProxmoxAPI):
            return prox

        storages = prox.nodes(config['proxmox_node']).storage.get()
        return [storage['storage'] for storage in storages]
    except:
        return None

def list_nodes(id):
    try:
        prox = get_proxmox(id=id, timeout=5)

        if not isinstance(prox, ProxmoxAPI):
            return prox

        return [node['node'] for node in prox.nodes.get()]
    except:
        return None

def list_isos(id):
    config = get_config(id)
    prox = get_proxmox(id)

    if not isinstance(prox, ProxmoxAPI):
        return prox

    iso_contents = prox.nodes(config['proxmox_node']).storage(config['proxmox_storage']).content.get(content='iso')
    return [iso['volid'] for iso in iso_contents]

def get_vm_status(id, vmid=None, config=None):
    if config is None:
        config = get_config(id)
    prox = get_proxmox(id)

    if not isinstance(prox, ProxmoxAPI):
        return prox

    if vmid is None:
        vmid = config['proxmox_vm_android_analysis_id']

    status = prox.nodes(config['proxmox_node']).qemu(vmid).status.current.get()
    return status.get('status', 'stopped')

def get_vm_ip(id, vmid=None):
    config = get_config(id)
    prox = get_proxmox(id)

    if not isinstance(prox, ProxmoxAPI):
        return prox

    if vmid is None:
        vmid = config['proxmox_vm_android_analysis_id']

    try:
        guest_agent_info = prox.nodes(config['proxmox_node']).qemu(vmid).agent('network-get-interfaces').get()

        for iface in guest_agent_info.get('result', []):
            for ip in iface.get('ip-addresses', []):
                if ip.get('ip-address') and ip.get('ip-address-type') == 'ipv4' and ip.get('ip-address') != '127.0.0.1':
                    return ip.get('ip-address')

    except Exception as e:
        return None
    return None

def wait_task(id, task_id):
    prox = get_proxmox(id)
    if not isinstance(prox, ProxmoxAPI):
        return prox

    config = get_config(id)
    while True:
        try:
            task_status = prox.nodes(config['proxmox_node']).tasks(task_id).status.get()
        except ConnectionError as e:
            task_status = {}

        if task_status.get('status') == 'stopped':
            if task_status.get('exitstatus') == 'OK':
                return True
            else:
                return False
        time.sleep(2) # 2 seconds

@shared_task
def create_vm(id, name):
    change_vm_step(id, 1)

    # reset error and event
    log_error_to_db(id, None)
    log_event_to_db(id, None)

    app_path = os.path.dirname(current_app.instance_path)

    # trying to make the operation atomic
    # repeatedly encounter dangling vm creation previously
    try:
        print('Downloading Ubuntu ISOs')
        download_ubuntu_iso_task = download_ubuntu_iso(id)
        print(download_ubuntu_iso_task)
        if download_ubuntu_iso_task != True:

            if not download_ubuntu_iso_task:
                log_error_to_db(id, 'Download ubuntu-24.04.1-live-server-amd64.iso to server failed.')
                change_vm_step(id, -1)
                return False

            wait_task(id, download_ubuntu_iso_task)

        print('Downloaded Ubuntu ISOs')
        change_vm_step(id, 2)

        print('Uploading NoCloud ISOs')
        upload_nocloud_iso_task = upload_nocloud_iso(id, app_path)
        if upload_nocloud_iso_task != True:
            if not upload_nocloud_iso_task:
                log_error_to_db(id, 'Upload nocloud iso image to server failed.')
                change_vm_step(id, -1)
                return False

            wait_task(id, upload_nocloud_iso_task)

        print('Uploaded NoCloud ISOs')
        change_vm_step(id, 3)

        print("Configure vm")
        config = get_config(id)
        iso_ubuntu = f"{config['proxmox_storage']}:iso/ubuntu-24.04.1-live-server-amd64.iso"
        iso_nocloud = f"{config['proxmox_storage']}:iso/nocloud-watcher-emulator.iso"
        bridge = config['proxmox_bridge']

        prox = get_proxmox(id)
        if not isinstance(prox, ProxmoxAPI):
            return prox

        existing_vms = [int(vm['vmid']) for vm in prox.cluster.resources.get(type='vm')]
        vmid = max(existing_vms, default=100)

        # observation shows proxmox create vm with vmid >= 100 by default
        if vmid < 100:
            vmid = 100
        vmid += 1

        prox.nodes(config['proxmox_node']).qemu.create(
            vmid=vmid,
            name=name,
            memory=config['proxmox_vm_android_analysis_memory'],
            cores=config['proxmox_vm_android_analysis_core'],
            cpu='host', # Needed for nested virtualization
            net0=f"virtio,bridge={bridge}",
            ide2=f'{iso_ubuntu},media=cdrom',
            ide1=f'{iso_nocloud},media=cdrom',
            scsihw="virtio-scsi-pci",
            scsi0=f"{config['proxmox_storage']}:{config['proxmox_vm_android_analysis_disk']},format=qcow2,cache=writethrough",
            boot="order=scsi0;ide2;ide1",
            bootdisk='scsi0',
            agent=1,
            start=1
        )

        while True:
            try:
                status = get_vm_status(id, vmid)
            except ConnectionError as e:
                print(e)
                status = None

            print(status)
            if status == 'running':
                try:
                    ip_address = get_vm_ip(id, vmid)
                except ConnectionError as e:
                    print(e)
                    ip_address = None
                except IndexError as e:
                    print(e)
                    continue

                print(ip_address)
                if ip_address:
                    # active
                    db = get_db()
                    db.execute(
                        'UPDATE config SET proxmox_vm_android_analysis_id = ?, proxmox_vm_android_analysis_name = ?, proxmox_vm_android_analysis_ip = ?'
                        ' WHERE id = ?',
                        (vmid, name, ip_address, id)
                    )
                    db.commit()
                    break
            time.sleep(5)

        # vm expected to be ready
        change_vm_step(id, 4)

        run_ansible_new_vms_status = False
        run_ansible_new_vms_count = 1
        while run_ansible_new_vms_status != True and run_ansible_new_vms_count < 10:
            run_ansible_new_vms_status = run_ansible_new_vms(
                db=get_db(),
                config_id=id,
                app_abs_path=os.path.abspath(app_path),
                host_address=ip_address,
                username='ubuntu',
                password='UbuntuWatcher',
            )
            if run_ansible_new_vms_status != True:
                log_event_to_db(id, "Ansible failed, retrying...")
                run_ansible_new_vms_count += 1
                time.sleep(1)

        if not run_ansible_new_vms_status:
            log_error_to_db(id, "VM's setup from ansible failed, tried 10 times.")
            change_vm_step(id, -1)
            return False

        change_vm_step(id, 5)
        return vmid
    except Exception as e:
        log_error_to_db(id, str(e))
        change_vm_step(id, -1)
        return False

"""
I use ubuntu-24.04.1-live-server ISO
"""
def ubuntu_iso_exists(id):
    iso_contents = list_isos(id)
    return any(iso.endswith('ubuntu-24.04.1-live-server-amd64.iso') for iso in iso_contents)

def download_ubuntu_iso(id):
    if ubuntu_iso_exists(id):
        return True

    config = get_config(id)
    prox = get_proxmox(id)
    if not isinstance(prox, ProxmoxAPI):
        return prox

    if prox is None:
        return False

    try:
        result = prox.nodes(config['proxmox_node']).storage(config['proxmox_storage'])('download-url').post(
            content='iso',
            filename='ubuntu-24.04.1-live-server-amd64.iso',
            url='https://linux.domainesia.com/ubuntu/iso-release/24.04.1/ubuntu-24.04.1-live-server-amd64.iso'
        )

        return result
    except Exception:
        return False

"""

"""
def nocloud_iso_exists(id):
    iso_contents = list_isos(id)
    return any(iso.endswith('nocloud-watcher-emulator.iso') for iso in iso_contents)

def upload_nocloud_iso(id, path):
    if nocloud_iso_exists(id):
        return True

    config = get_config(id)
    prox = get_proxmox(id)

    if not isinstance(prox, ProxmoxAPI):
        return prox

    f = open(
        os.path.join(
            path,
            'instance-setup',
            'watcher-emulator',
            'nocloud-watcher-emulator.iso'
        ),
        'rb'
    )

    try:
        prox.nodes(config['proxmox_node']).storage(config['proxmox_storage']).upload.post(
            content='iso',
            filename=f,
        )

        return True
    except Exception:
        return False

"""
Basically if VM somehow is turned off, force start it.
"""
@shared_task
def force_start_vm(id):
    # reset ip so it does not get queried
    db = get_db()
    db.execute(
        'UPDATE config SET proxmox_vm_android_analysis_ip = ?'
        ' WHERE id = ?',
        (None, id)
    )
    db.commit()

    config = get_config(id=id)

    prox = get_proxmox(id)
    if not isinstance(prox, ProxmoxAPI):
        return prox

    vmid = config['proxmox_vm_android_analysis_id']
    node = config['proxmox_node']

    try:
        prox.nodes(node).qemu(vmid).status.start.post()
    except Exception:
        return False

    while True:
        try:
            status = get_vm_status(id, vmid)
        except ConnectionError as e:
            print(e)
            status = None

        print(status)
        if status == 'running':
            try:
                ip_address = get_vm_ip(id, vmid)
            except ConnectionError as e:
                print(e)
                ip_address = None
            except IndexError as e:
                print(e)
                continue

            print(ip_address)
            if ip_address:
                # active
                db = get_db()
                db.execute(
                    'UPDATE config SET proxmox_vm_android_analysis_ip = ?'
                    ' WHERE id = ?',
                    (ip_address, id)
                )
                db.commit()
                break
        time.sleep(5)

    return True

"""
Basically if VM somehow acting weird, reset it.
Reset as in force turn off and back on, not deleting data.
"""
@shared_task
def force_reset_vm(id):
    # reset ip so it does not get queried
    db = get_db()
    db.execute(
        'UPDATE config SET proxmox_vm_android_analysis_ip = ?'
        ' WHERE id = ?',
        (None, id)
    )
    db.commit()

    config = get_config(id=id)

    prox = get_proxmox(id)
    if not isinstance(prox, ProxmoxAPI):
        return prox

    vmid = config['proxmox_vm_android_analysis_id']
    node = config['proxmox_node']

    try:
        prox.nodes(node).qemu(vmid).status.reset.post()
    except Exception:
        return False

    while True:
        try:
            status = get_vm_status(id, vmid)
        except ConnectionError as e:
            print(e)
            status = None

        print(status)
        if status == 'running':
            try:
                ip_address = get_vm_ip(id, vmid)
            except ConnectionError as e:
                print(e)
                ip_address = None
            except IndexError as e:
                print(e)
                continue

            print(ip_address)
            if ip_address:
                # active
                db = get_db()
                db.execute(
                    'UPDATE config SET proxmox_vm_android_analysis_ip = ?'
                    ' WHERE id = ?',
                    (ip_address, id)
                )
                db.commit()
                break
        time.sleep(5)

    return True

@shared_task
def delete_vm(id):
    config = get_config(id=id)

    db = get_db()
    db.execute(
        'UPDATE config SET is_deleted_from_proxmox=1'
        ' WHERE id = ?',
        (id,)
    )
    db.commit()

    prox = get_proxmox(id)
    if not isinstance(prox, ProxmoxAPI):
        # Dangling VM creation, previously failed. Ignore.
        return prox

    vmid = config['proxmox_vm_android_analysis_id']
    node = config['proxmox_node']

    # Next until end requires valid proxmox node and vmid,
    # but when it fails the vm is already flagged as deleted  anyway (above)
    try:
        prox.nodes(node).qemu(vmid).status.stop.post()
    except Exception as e:
        return False

    # make sure vm is really stopped, scared because deletion might occur when vm is still running
    while True:
        try:
            status = get_vm_status(id, vmid, config)
        except ConnectionError as e:
            status = None
        except Exception as e:
            print(e)
            time.sleep(2)
            continue

        print(status)
        if status == 'stopped':
            break

        time.sleep(2)

    while True:
        try:
            prox.nodes(node).qemu(vmid).delete()
        except Exception as e:
            print(e)
            time.sleep(2)
            continue
        break

    return True
