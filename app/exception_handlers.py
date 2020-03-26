from app import app, db, tasks
from app.models import User, Post, Streaming


def my_handler(job, exc_type, exc_value, traceback):
        stream = Streaming(job_id='peine')
        db.session.add(stream)
        db. session.commit()