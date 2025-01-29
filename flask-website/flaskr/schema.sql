DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS android_app;
DROP TABLE IF EXISTS dynamic_analysis_task;
DROP TABLE IF EXISTS dynamic_analysis_app;
DROP TABLE IF EXISTS dynamic_analysis_log;
DROP TABLE IF EXISTS config;
DROP TABLE IF EXISTS queue_dynamic_analysis_task;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE android_app (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    app_name TEXT NOT NULL,
    package_name TEXT NOT NULL,
    filename TEXT NOT NULL,
    is_deleted BOOLEAN DEFAULT 0,
    is_hidden_dynamic_analysis_task BOOLEAN DEFAULT 0,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id)
);

CREATE TABLE dynamic_analysis_task (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    sdk_level INTEGER NOT NULL,
    run_package TEXT NOT NULL,
    watch_packages TEXT NOT NULL,
    is_manual_control BOOLEAN NOT NULL,
    no_internet BOOLEAN NOT NULL,
    start_session TIMESTAMP,
    end_session TIMESTAMP,
    session_duration INTEGER NOT NULL,
    vnc_password TEXT NOT NULL,
    event_message TEXT,
    error_message TEXT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (config_id) REFERENCES config(id)
);

CREATE TABLE dynamic_analysis_app (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dynamic_analysis_task_id INTEGER NOT NULL,
    android_app_id INTEGER NOT NULL,
    FOREIGN KEY (dynamic_analysis_task_id) REFERENCES dynamic_analysis_task(id) ON DELETE CASCADE,
    FOREIGN KEY (android_app_id) REFERENCES android_app(id)
);

-- log_timestamp from watcher hook is from System.currentTimeMillis()
-- log_timestamp from time milis: datetime.datetime.utcfromtimestamp(current_seconds / 1000).strftime("%Y-%m-%d %H:%M:%S")
CREATE TABLE dynamic_analysis_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dynamic_analysis_task_id INTEGER NOT NULL,
    log_type TEXT NOT NULL,
    log_action TEXT NOT NULL,
    log_msg TEXT NOT NULL,
    log_data TEXT,
    log_timestamp TIMESTAMP,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dynamic_analysis_task_id) REFERENCES dynamic_analysis_task_id(id) ON DELETE CASCADE
);

-- First time setup this will be empty
-- step INTEGER NOT NULL related to the form wizard, like first time setup
-- current_activity TEXT vm things step
-- error_message TEXT, -- only looked if vm_step or step is -1
CREATE TABLE config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    step INTEGER NOT NULL,
    vm_step INTEGER, 
    event_message TEXT,
    error_message TEXT,
    is_deleted_from_proxmox BOOLEAN,
    proxmox_host_address TEXT,
    proxmox_account_realm TEXT,
    proxmox_account_username TEXT,
    proxmox_account_password TEXT,
    proxmox_node TEXT,
    proxmox_storage TEXT,
    proxmox_bridge TEXT,
    proxmox_vm_android_analysis_id TEXT,
    proxmox_vm_android_analysis_name TEXT,
    proxmox_vm_android_analysis_ip TEXT,
    proxmox_vm_android_analysis_memory INTEGER,
    proxmox_vm_android_analysis_core INTEGER,
    proxmox_vm_android_analysis_disk INTEGER,
    lock_dynamic_analysis_task_id INTEGER,
    FOREIGN KEY (lock_dynamic_analysis_task_id) REFERENCES dynamic_analysis_task_id(id)
);

CREATE TABLE queue_dynamic_analysis_task (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dynamic_analysis_task_id INTEGER NOT NULL,
    FOREIGN KEY (dynamic_analysis_task_id) REFERENCES dynamic_analysis_task(id) ON DELETE CASCADE
);


-- Enable foreign keys RRAAAAHHHH!
PRAGMA foreign_keys = ON;