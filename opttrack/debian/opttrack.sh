#!/bin/bash

# Usage:
# $ sudo ./opttrack.sh --start
# $ sudo ./opttrack.sh --stop

while :;
do
    case "$1" in
        --start)
            action='start'
            break
            ;;
        --stop)
            action='stop'
            break
            ;;
        *)
            echo 'unknown option: '$1
            echo "Possible options are '--start' and '--stop'"
            break
            ;;
    esac
done


DAEMON_USER="opttrack"
DAEMON_GROUP="$DAEMON_USER"
CMD=/home/$DAEMON_USER/.virtualenvs/opttrack/bin/python
SERVICE="/home/$DAEMON_USER/workspace/opttrack/opttrack/quote_service.py"
PIDFILE="/var/run/$DAEMON_USER.pid"

start_server() {
    start-stop-daemon --background --start --verbose --pidfile $PIDFILE \
        --make-pidfile --chuid $DAEMON_USER:$DAEMON_GROUP \
        --exec $CMD $SERVICE
    errcode=$?
    return $errcode
}

stop_server() {
    # Stop the process using the wrapper
    start-stop-daemon --stop --verbose --pidfile $PIDFILE \
        --retry 300 \
        --user $DAEMON_USER \
        --exec $CMD $SERVICE
    errcode=$?
    return $errcode
}

echo "$action"

case "$action" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    *)
        echo "Invalid action: ${action}"
        exit 1
        ;;
esac

exit 0
