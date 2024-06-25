#!/bin/sh

python manage.py migrate

# Run server command
python manage.py runserver 0.0.0.0:8000
