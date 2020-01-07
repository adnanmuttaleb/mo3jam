FROM python:3.7.0

ENV GROUP_ID=1000 \
    USER_ID=1000

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY . /app

RUN groupadd -g $GROUP_ID www
RUN useradd -u $USER_ID -g www -s /bin/sh www

USER www

EXPOSE 5000

