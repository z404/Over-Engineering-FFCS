cd OE_FFCS
python.exe manage.py makemigrations
python.exe manage.py migrate --run-syncdb
python.exe manage.py runserver