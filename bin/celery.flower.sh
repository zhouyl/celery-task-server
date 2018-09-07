#!/bin/bash

############################################################
#
# Celery Task 任务服务 WEB 管理后台
#
############################################################

source $(dirname "$0")/celery.profile.sh

name="Celery Tasks Web Interface (Flower Extension)"
port=5555
log_level=info
log_file="$log_path/celery.flower.log"
pid_file="$pid_path/celery.flower.pid"

start() {
    # --persistent --inspect --inspect-timeout=3000
    $celery_bin flower --workdir=$workdir --app=$application --port=$port \
        --logfile=$log_file --logging=$log_level >> $log_file 2>> $log_file &

    # 写入 pid 文件
    ps -ef | grep flower | grep $port | grep $application | awk '{print $2}' > $pid_file

    echo -e "\033[32m$name started.\033[0m"

    return 0
}

stop() {
    if status ; then
        pid=`cat "$pid_file"`
        echo -e "\033[33mKilling $name (pid $pid) with SIGTERM.\033[0m"
        kill -TERM $pid

        # Wait for it to exit.
        for i in 1 2 3 4 5 6 7 8 9 ; do
            echo -e "\033[33mWaiting $name (pid $pid) to die...\033[0m"
            status || break
            sleep 1
        done

        if status ; then
            echo -e "\033[31m$name stop failed; still running.\033[0m"
            return 1 # stop timed out and not forced
        else
            rm -f $pid_file
            echo -e "\033[32m$name stopped.\033[0m"
        fi
    else
        echo -e "\033[31m$name is not running.\033[0m"
    fi
}

force_stop() {
    if status ; then
        pid=`cat "$pid_file"`
        echo -e "\033[33mKilling $name (pid $pid) with SIGKILL.\033[0m"
        kill -SIGKILL $pid

        rm -f $pid_file
        echo -e "\033[32m$name force stopped.\033[0m"
    else
        echo -e "\033[31m$name is not running.\033[0m"
    fi
}

status() {
    if [ -f "$pid_file" ] ; then
        pid=`cat "$pid_file"`
        if kill -0 $pid > /dev/null 2> /dev/null ; then
            # process by this pid is running.
            # It may not be our pid, but that's what you get with just pidfiles.
            # TODO(sissel): Check if this process seems to be the same as the one we
            # expect. It'd be nice to use flock here, but flock uses fork, not exec,
            # so it makes it quite awkward to use in this case.
            return 0
        else
            rm -f $pid_file
            return 2 # program is dead but pid file exists
        fi
    else
        return 3 # program is not running
    fi
}

case "$1" in
    start)
        status
        code=$?
        if [ $code -eq 0 ]; then
            echo -e "\033[33m$name is already running.\033[0m"
        else
            start
            code=$?
        fi

        exit $code
        ;;

    stop)
        stop
        ;;

    force-stop)
        force_stop
        ;;

    restart)
        stop && start
        ;;

    status)
        status
        code=$?
        if [ $code -eq 0 ] ; then
            echo -e "\033[32m$name is running.\033[0m"
        else
            echo -e "\033[31m$name is not running.\033[0m"
        fi

        exit $code
        ;;

    *)

        echo "Usage: $0 {start|stop|force-stop|status|restart}" >&2
        exit 3
    ;;
esac

exit $?
