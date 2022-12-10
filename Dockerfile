FROM python:3.8.15

EXPOSE 8000

RUN pip install --upgrade pip

RUN apt update && apt install libdbus-1-dev libdbus-glib-1-dev -y

COPY left-requirements.txt ./left-requirements.txt

RUN pip install -r left-requirements.txt

COPY 3.8requirements.txt ./3.8requirements.txt

RUN pip install -r 3.8requirements.txt

COPY . .

RUN python3 OE_FFCS/manage.py makemigrations
RUN python3 OE_FFCS/manage.py migrate --run-syncdb

CMD ["python3", "OE_FFCS/manage.py", "runserver", "0.0.0.0:8001"]
