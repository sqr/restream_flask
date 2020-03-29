from app import app, db
from rq import get_current_job
from app.models import Task, Streaming
import time
import ffmpeg
import youtube_dl

def get_manifest(video_url):
    ydl_opts = {
        'format': 'best'
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        peine = ydl.extract_info(video_url, download=False)

    return peine.get('url')

def generate_url(server, stream_key):
    return server + "/" + stream_key

def restream(origin, server, stream_key):
    stream_server = generate_url(server, stream_key)
    try:
        stream_map = None
        stream1 = ffmpeg.input(get_manifest(origin))
        stream2 = ffmpeg.input('mosca_66.png')
        stream_ol = ffmpeg.overlay(stream1, stream2, x='main_w-overlay_w-50', y='50')
        stream_ol = ffmpeg.filter(stream_ol, 'fps', fps=25, round='up')
        a1 = stream1.audio
        stream = ffmpeg.output(stream_ol, a1, stream_server, format='flv', vcodec='libx264', s='1280x720', acodec='aac', preset='veryfast', g='50', crf='23', maxrate='4M', bufsize='5M', channel_layout='stereo')
        print(stream.get_args())
        ffmpeg.run(stream)
        set_complete()
    except:
        set_complete() 

def example(seconds, otherseconds):
    print('Starting task')
    try:
        timeseconds = int(seconds)+int(otherseconds)
        for i in range(timeseconds):
            print(i)
            time.sleep(1)
        print('Task completed')
        set_complete()
    except:
        set_complete()


def set_complete():
    job = get_current_job()
    if job:
        task = Streaming.query.filter_by(job_id=job.get_id()).first()
        task.complete = True
        db.session.commit()
