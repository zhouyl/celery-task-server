#!/bin/bash

root=$(cd "$(dirname "$0")"; cd ..; pwd)
workdir="$root/app"
application=tasks
log_level=info
log_path="$root/logs/$(date +%Y%m%d)"
pid_path="/tmp/celery-task-server"
celery_bin="$root/venv/bin/celery"

# 检查环境可用性
if [ ! -f $celery_bin ] ; then
    echo "Please install celery in virtualenv & setup this application!"
    exit 0
fi

# 生产环境，强制日志级别为 info
if [ -f /etc/php.env.production ] ; then
    log_level=info
fi

# 检查并创建日志目录
if [ ! -d $log_path ] ; then
    mkdir -p $log_path
fi

# 检查并创建进程文件目录
if [ ! -d $pid_path ] ; then
    mkdir -p $pid_path
fi
