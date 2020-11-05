#!/bin/sh
flask db upgrade
exec rq worker microblog-tasks --url redis://redis:6379
