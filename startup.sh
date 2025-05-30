#!/bin/sh
set -e

# 获取环境变量
T_TOKEN=${T_TOKEN:-default_token}
C_TOKEN=${C_TOKEN:-default_client_id}

# 执行你的命令
python3 web.py -p=8000 -t="$T_TOKEN" -c="$C_TOKEN" -a=VlistlBRh3A7ent3S3rq6A1WYHoyjEuqIU01GeuLzK9