#!/bin/sh

python manage.py migrate

# Collect static files for web server to serve
python manage.py collectstatic --no-input

# Run server command, "application" is the variable name in SakanaRM/wsgi.py
gunicorn SakanaRM.wsgi:application --bind 0.0.0.0:8000
