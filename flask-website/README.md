This is web side of things. The web handles android sandbox deployment to PVE, configured with NoCloud Cloud-Init and then Ansible. Configuration is done this way because Cloud-Init installation or configuration process cannot be requested to be shown to users, while Ansible's current task can be requested via Ansible Runner's callback.

To run the web, you need to install needed dependencies. This can be done via executing `install-needed-pkg.sh`. This script assumes you are on a linux distro that is configured to use `apt`. If you don't use `apt`, find a way to install:

- python3
- python3-pip
- python3-venv
- sshpass

After installing the dependencies, create virtual environment using name `venv` with `python3-venv`. When virtual environment configuration is done, run `./venv/bin/pip install -r requirements.txt` to install python dependencies used by the web.

Web will be run by using `supervisord` via python. Before starting the web, execute `init_db.sh` first so that the database is initialized. Here is list of script and it's description related to web's `supervisord` script:

- `start-supervisord.sh`: Starting the web and it's services.
- `stop-supervisord.sh`: Stopping the web and it's services.
- `restart-supervisord.sh`: Restarting the web and it's services.
- `shutdown-supervisord.sh`: Stopping the web, it's services, and clear file used by `supervisord`.

The web consist of 3 main services that needs to run:

1. Celery: To run process in the background.
1. Websockify: Connecting sandbox's VNC to NoVNC via websocket.
1. Flask's app: The web's flask process.

By default, files related to web's database, upload, log, celery's database, and websockify's token are stored on `instance` directory.

More complete list of dependencies that is used in web side of things:

1. SQLite
1. Python
1. Flask
1. Celery
1. SQLAlchemy
1. Proxmoxer
1. Ansible
1. Ansible
1. Sshpass
1. Pyaxmlparser
1. Supervisor
1. Websockify
1. NoVNC
1. DataTables
1. Ansi2html

If explanation on this readme doesn't suffice, please open an issue to discuss it publicly.
