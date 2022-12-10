cd OE_FFCS
python3.8 manage.py makemigrations
python3.8 manage.py migrate --run-syncdb
python3.8 manage.py runserver
