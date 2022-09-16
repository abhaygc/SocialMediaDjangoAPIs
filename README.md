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

## CREATE USER
POST /api/register/ 
  INPUT - NAME, EMAIL, PASSWORD
  RETURN - ID, NAME, EMAIL
## LOGIN/AUTHENTICATE
POST /api/authenticate/
  INPUT - EMAIL, PASSWORD
  RETURN - jwt 

