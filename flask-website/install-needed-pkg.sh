#!/bin/sh

sudo apt-get install -y python3 python3-pip python3-venv sshpass
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
