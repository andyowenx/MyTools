#!/bin/bash
### BEGIN INIT INFO
# Provides:          owen
# Default-Start:     2 3 4 5
# Default-Stop:
# Short-Description: Broadcast device IP
# Description:       It will auto broadcast device IP to UDP port 50022
### END INIT INFO

start() {
	/root/broadcast_ip.py
}

# Restart the service FOO
stop() {
	killall broadcast_ip.py
}

### main logic ###
case "$1" in
    start)
	start
	;;
    stop)
	stop
	;;
    status)
	;;
    restart|reload|condrestart)
	stop
	start
	;;
    *)
    echo $"Usage: $0 {start|stop|restart|reload|status}"
	exit 1
    esac

exit 0
