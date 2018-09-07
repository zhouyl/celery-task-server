#!/usr/bin/env bash

cd $(dirname "$0")

############################################################
#
# Celery Task Server 管理脚本(集中管理 worker & beat scheduler)
#
############################################################

start() {
    bash celery.worker.sh start
    bash celery.beat.sh start
}

stop() {
    bash celery.worker.sh stop
    bash celery.beat.sh stop
}

force_stop() {
    bash celery.worker.sh force-stop
    bash celery.beat.sh force-stop
}

restart() {
    bash celery.worker.sh restart
    bash celery.beat.sh restart
}

status() {
    bash celery.worker.sh status
    bash celery.beat.sh status
}

case "$1" in
    start)
        start
        ;;

    stop)
        stop
        ;;

    force-stop)
        force_stop
        ;;

    restart)
        restart
        ;;

    status)
        status
        ;;

    *)

        echo "Usage: $0 {start|stop|force-stop|status|reload|restart}" >&2
        exit 3
    ;;
esac

exit $?