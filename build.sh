#!/usr/bin/env bash
set -o errexit

# 安装依赖
pip install -r requirements.txt

# 收集静态文件
python manage.py collectstatic --no-input

# 迁移数据库
python manage.py migrate
