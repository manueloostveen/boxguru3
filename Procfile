release: python manage.py migrate
release: python products/populate_db.py
web: gunicorn boxguru.wsgi --log-file -