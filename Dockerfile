FROM python:3.8.1-alpine

RUN adduser -D streaming

WORKDIR /home/streaming

COPY requirements.txt requirements.txt
RUN apk update && apk add gcc libc-dev make git libffi-dev openssl-dev python3-dev libxml2-dev libxslt-dev
RUN pip install -r requirements.txt
RUN pip install gunicorn pymysql

COPY app app
COPY migrations migrations
COPY microblog.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP microblog.py

RUN chown -R streaming:streaming ./
USER streaming

EXPOSE 5000
ENTRYPOINT ["sh","./boot.sh"]