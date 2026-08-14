#!/bin/bash

APP_PORT=${PORT:-8000}

mkdir /var/lib/littlepequi
echo $GCS_KEY_FILE|base64 --decode > /var/lib/littlepequi/little-pequi-gcs.json

cd /app/

/opt/venv/bin/python manage.py migrate --noinput
/opt/venv/bin/python manage.py deploy_superuser
/opt/venv/bin/python manage.py loaddata api/fixtures/categories.json
/opt/venv/bin/python manage.py loaddata api/fixtures/tags.json
/opt/venv/bin/python manage.py loaddata api/fixtures/menuitems.json
/opt/venv/bin/gunicorn --worker-tmp-dir /dev/shm backend.wsgi:application --bind "0.0.0.0:${APP_PORT}"
