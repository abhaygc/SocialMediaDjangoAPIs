#!/usr/bin/env bash
set -e # exit on error

pip3 install -r requirements.txt

python manage.py makemigrations
python manage.py makemigrations social_media
python manage.py migrate --no-input