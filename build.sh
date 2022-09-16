#!/usr/bin/env bash
set -e # exit on error

pip3 install -r requirements.txt

# sudo service postgresql start

sudo -u postgres psql -c "CREATE DATABASE social;"
sudo -u postgres psql -c "CREATE USER admin WITH ENCRYPTED PASSWORD 'admin';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE social TO admin;"
sudo -u postgres psql -c "ALTER ROLE admin CREATEDB;"

echo `ls -l`

echo "Making Migrations"
python manage.py makemigrations

echo "Making Migrations for social_media"
python manage.py makemigrations social_media

echo "Echo executing migrate"
python manage.py migrate --no-input

