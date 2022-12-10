FROM python:3.8.15

EXPOSE 8000

RUN pip install --upgrade pip

RUN apt update && apt install libdbus-1-dev libdbus-glib-1-dev -y

COPY requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY . .

RUN python3 OE_FFCS/manage.py makemigrations
RUN python3 OE_FFCS/manage.py migrate --run-syncdb

ARG DJANGO_SUPERUSER_USERNAME=admin
ARG DJANGO_SUPERUSER_EMAIL=admin@example.com
ARG DJANGO_SUPERUSER_PASSWORD=admin123
RUN python3 OE_FFCS/manage.py createsuperuser --noinput

CMD ["python3", "OE_FFCS/manage.py", "runserver", "0.0.0.0:8001"]
