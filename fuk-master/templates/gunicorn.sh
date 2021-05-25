#!/bin/bash
# gunicorn template
set -e
LOGFILE=../logs/fuk-%(environment)s.log
NUM_WORKERS=3
# user/group to run as
USER=www-data
GROUP=www-data
export PYTHONPATH=%(code_root)s
export DJANGO_SETTINGS_MODULE=settings.%(environment)s
cd %(code_root)s
source ../%(project)s-env/bin/activate
exec ../%(project)s-env/bin/gunicorn_django -w $NUM_WORKERS \
--user=$USER --group=$GROUP --log-level=info --bind=127.0.0.1:%(wsgi_port)s \
--log-file=$LOGFILE 2>>$LOGFILE 