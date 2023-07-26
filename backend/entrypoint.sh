#!/bin/bash
python -m gunicorn --bind 0.0.0.0:8000 foodgram.wsgi
python backend/manage.py migrate
python backend/manage.py collectstatic
cp -r /app/collected_static/. /static/static/
