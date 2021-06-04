cd OE_FFCS
python3 manage.py makemigrations
python3 manage.py migrate --run-syncdb
python3 manage.py runserver