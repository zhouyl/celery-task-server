#!/bin/bash

###############################################################################
#
# Celery Task Worker 进程管理脚本 (不包括 beat scheduler 服务)
#
# 虽然可以直接在该脚本中集成 beat scheduler 服务，但不建议这样做
#
# 分开管理的优势在于，我们可以仅停掉 beat scheduler，而保持 worker 的正常运行！
#
###############################################################################

source $(dirname "$0")/celery.profile.sh

name="Celery Tasks Worker"
hostname="celery-task-server"
pid_file="$pid_path/celery.worker.%N.pid"
log_file="$log_path/celery.worker.%N.log"

# 非生产环境下，日志集中在一个文件中，方便定位调试
if [ ! -f /etc/php.env.production ] ; then
    log_file="$log_path/celery.worker.log"
fi

###############################################################################
# 网络性能参数
# 具体性能参数调优，请使用 flower 或者 celery inspect 监控后进行调整
###############################################################################
# prefork: 进程派生模式, 不要超过 20 个子进程，更多的需求请增加 workers，性能不佳
# gevent: 基于协程的并发模式，epoll监听机制，建议并发数配置不超过 5000
# eventlet: 基于协程的并发模式，建议并发数配置不超过 5000
pool=gevent # gevent 性能更好，eventlet 稳定性更佳
workers="w1 w2 w3 w4 w5" # worker 名称，建议不要超过 10 个
concurrency=300 # 每个 worker 默认启动并发数
max_concurrency=500 # 最大并发数，prefork 模式不超过 20，gevent/eventlet 不超过 5000
min_concurrency=200 # 最小并发数，不建议跟最大数差距过大，以避免队列堵塞

# 服务启动参数
daemon_opts="--workdir=$workdir --app=$application --events --hostname=$hostname --heartbeat-interval=1 \
    --pool=$pool --concurrency=$concurrency --autoscale=$max_concurrency,$min_concurrency \
    --loglevel=$log_level --pidfile=$pid_file --logfile=$log_file "

start() {
    $celery_bin multi start $workers $daemon_opts

    echo -e "\033[32m$name started.\033[0m"

    return 0
}

stop() {
    $celery_bin multi stopwait $workers $daemon_opts

    echo -e "\033[32m$name stopped.\033[0m"
}

force_stop() {
    $celery_bin multi stop $workers $daemon_opts

    echo -e "\033[32m$name force stopped.\033[0m"
}

restart() {
    $celery_bin multi restart $workers $daemon_opts
    echo -e "\033[32m$name restarted.\033[0m"
}

status() {
    $celery_bin multi show $workers
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

    reload)
        restart
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
