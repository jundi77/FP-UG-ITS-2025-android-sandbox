#!/bin/bash

source ./venv/bin/activate
SUPERVISOR_CONF="./supervisord.conf"

if [ "$1" = "--debug" ]; then
    SUPERVISOR_CONF="./supervisord_debug.conf"
    echo "[DEBUG]: $SUPERVISOR_CONF"
fi

./venv/bin/supervisord -c $SUPERVISOR_CONF
./venv/bin/supervisorctl -c $SUPERVISOR_CONF start all
