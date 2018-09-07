#!/bin/bash

############################################################
#
# Celery Task 服务事件管理工具
#
############################################################

source $(dirname "$0")/celery.profile.sh

$celery_bin --workdir=$workdir --app=$application $*
