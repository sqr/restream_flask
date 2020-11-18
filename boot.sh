#!/bin/sh
flask db upgrade
exec gunicorn -k gevent -b :5000 --access-logfile - --error-logfile - microblog:app