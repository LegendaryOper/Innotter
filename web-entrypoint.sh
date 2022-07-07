poetry run ./manage.py migrate
poetry run ./manage.py createsuperuser --noinput --username admin --email a@gmail.com
poetry run ./manage.py runserver 0.0.0.0:8000