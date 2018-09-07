#!/usr/bin/env bash

root=$(cd "$(dirname "$0")"; cd ../; pwd)
logfile=$root/logs/`date +%Y%m%d`/daemon-service.log
python=$root/venv/bin/python

# 待守护的命令列表
commands=(
    "$python $root/app/command.py my:task"
)

# 创建日志文件目录
logdir=$(dirname $logfile)
if [ ! -d $logdir ]; then
    mkdir -p $logdir
    chmod ugo+w $logdir # 保证日志目录能够写入
fi

start() {
    for ((i = 0; i < ${#commands[@]}; i++)) ; do
        cmd=${commands[$i]}
        pid=$(pgrep -f "$cmd")
        if [ "$pid" ] ; then
            echo -e "$cmd ($pid)  \033[33;49;2m[ RUNNING ]\033[39;49;0m"
        else
            $cmd >> /dev/null &
            echo -e "$cmd  \033[32;49;2m[ STARTED ]\033[39;49;0m"
            echo -e "$(date +'%Y-%m-%d %H:%M:%S') $cmd started." >> $logfile
        fi
    done

    return 0
}

stop() {
    for ((i = 0; i < ${#commands[@]}; i++)) ; do
        cmd=${commands[$i]}
        pid=$(pgrep -f "$cmd")
        if [ "$pid" ] ; then
            kill -15 $pid
            echo -e "$cmd ($pid)  \033[31;49;2m[ KILLED ] \033[39;49;0m"
            echo -e "$(date +'%Y-%m-%d %H:%M:%S') $cmd killed." >> $logfile
        else
            echo -e "$cmd  \033[37;49;2m[ NONE ]\033[39;49;0m"
        fi
    done
}

status() {
    echo "Process status list:"
    for ((i = 0; i < ${#commands[@]}; i++)) ; do
        cmd=${commands[$i]}
        pid=$(pgrep -f "$cmd")
        if [ "$pid" ] ; then
            echo -e "$cmd ($pid)  \033[33;49;2m[ RUNNING ]\033[39;49;0m"
        else
            echo -e "$cmd  \033[37;49;2m[ NONE ]\033[39;49;0m"
        fi
    done
}


case "$1" in
    start)
        start
        ;;

    stop)
        stop
        ;;

    status)
        status
        ;;

    restart)
        stop && start
        ;;

    *)
        echo -e "Usage: $0 [start|stop|status|restart]\n"
        status
        ;;
esac

exit $?
