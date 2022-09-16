# SocialMediaDjangoAPIs


Environment:
python -m venv env

Activate Environment:
env\Scripts\activate

Build:
pip install -r requirements.txt

python manage.py makemigrations
python manage.py makemigrations social_media
python manage.py migrate

Test:
python manage.py test social_media

Run:
python manage.py runserver