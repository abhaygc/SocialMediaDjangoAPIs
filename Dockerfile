FROM python:3 AS base
LABEL maintainer="ABHAY GUPTA"

WORKDIR /app
ADD /social_media ./social_media
COPY ./requirements.txt ./
COPY ./build.sh ./
COPY ./manage.py ./
COPY ./README.md ./
RUN chmod u+x build.sh

RUN apt-get update && apt-get -y install sudo
RUN apt-get update && apt-get -y install gnupg2 lsb-release
RUN apt-get update && apt-get -y install tree
RUN apt-get update && apt-get -y install postgresql postgresql-contrib

RUN sudo service postgresql start
RUN sudo ./build.sh
RUN python manage.py test social_media

EXPOSE 8000
CMD ["python", "manage.py", "runserver"]


# docker build -t socialMediaApi





