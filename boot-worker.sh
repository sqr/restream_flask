#!/bin/sh
flask db upgrade
exec rq worker microblog-tasks --job-class=app.stop_job.StopJob --worker-class=app.stop_job.PubSubWorker --url redis://redis:6379