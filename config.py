import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess-lolete'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE = 3
    STREAMINGS_PER_PAGE = 10
    REDIS_URL = 'redis://192.168.1.147:6380'

#    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://:PeinesitoPeinador2020$@sqrsrv.no-ip.org:6379/0'
