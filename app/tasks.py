from rq import queue
from app import app, db
from rq import get_current_job, Queue
from rq.worker import Worker, WorkerStatus
from app.models import Task, Streaming
import time
import ffmpeg
import youtube_dl
from pathlib import Path
import json
from redis import Redis


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
    job = get_current_job()
    job_id = job.get_id()
    task = Streaming.query.filter_by(job_id=job_id).first()
    task_name = task.title
    r = Redis.from_url(app.config['REDIS_URL'], charset='utf-8', decode_responses=True)


    if 'youtu' in origin:
        for i in range(3):
            try:
                origin = get_manifest(origin)
            except Exception as e:
                print(e)
                continue
            else:
                break
        else:
            set_complete(job_id)
            r.publish('error', 'Error parseando youtube en: '+task_name)
            return

    stream_server = generate_url(server, stream_key)
    try:
        stream_map = None
        probe_decoded = probe(origin)
        video_stream = get_video_stream(probe_decoded)
        audio_stream = get_audio_stream(probe_decoded)
        stream1 = ffmpeg.input(origin)
        stream2 = ffmpeg.input('mosca_76.png')
        stream2 = ffmpeg.filter(stream2, 'scale', w='-1', h=video_stream[2])
        stream_ol = ffmpeg.overlay(stream1[str(video_stream[0])], stream2, x='main_w-overlay_w')
        stream_ol = ffmpeg.filter(stream_ol, 'fps', fps=25, round='up')
        a1 = stream1.audio
        stream1_audio = stream1[str(audio_stream)]
        if 'dailymotion' in server:
            stream = ffmpeg.output(stream_ol, stream1_audio, stream_server, format='flv', vcodec='libx264', acodec='aac', preset='veryfast', g='50', threads='2', s='1920x1080', crf='23', maxrate='4M', bufsize='5M', channel_layout='stereo')
        else:
            stream = ffmpeg.output(stream_ol, stream1_audio, stream_server, format='flv', vcodec='libx264', acodec='aac', preset='veryfast', g='50', threads='2', s='1280x720', crf='23', maxrate='4M', bufsize='5M', channel_layout='stereo')
        ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
        print('job completed')
        set_complete(job_id)
    except ffmpeg.Error as e:
        print('stdout:', e.stdout.decode('utf8'))
        print('stderr:', e.stderr.decode('utf8'))
        e_decoded = e.stderr.decode('utf8')
        if '404 Not Found' in e_decoded:
            r.publish('error', 'El stream ' + task_name + ' ha terminado.')
        else:
            r.publish('error', 'Error desconocido en stream: ' + task_name)
        set_complete(job_id)
        raise e
 

def set_complete(jobid):
    if jobid:
        task = Streaming.query.filter_by(job_id=jobid).first()
        task.complete = True
        db.session.commit()

def probe(url):
    probe_encoded = json.dumps(ffmpeg.probe(url))
    return json.loads(probe_encoded)

def get_video_stream(probe_decoded):
    video_stream = 0
    video_width = 0
    video_height = 0
    for streams in probe_decoded['streams']:
        if streams['codec_type'] == 'video':
            if streams['height'] >= video_height:
                video_height = streams['height']
                video_width = streams['width']
                video_stream = streams['index']
    return (video_stream, video_width, video_height)

def get_audio_stream(probe_decoded):
    audio_stream = 0
    audio_bitrate = 0
    for streams in probe_decoded['streams']:
        if streams['codec_type'] == 'audio':
            try:
                if int(streams['bit_rate']) >= audio_bitrate:
                    audio_stream = streams['index']
            except KeyError:
                try:
                    if int(streams['tags']['variant_bitrate']) >= audio_bitrate:
                        audio_stream = streams['index']
                except KeyError:
                    audio_stream = 1
    return audio_stream

def stream_started(id):
    task = Streaming.query.filter_by(job_id=id).first()
    if task.complete == True:
        return False
    else:
        return True

def worker_availability():
    redis = Redis.from_url(app.config['REDIS_URL'])
    queue = Queue('microblog-tasks', connection=redis)
    worker_array = {'total': 0, 'busy': 0, 'idle': 0}
    workers = Worker.all(connection=redis, queue=queue)
    for worker in workers:
        worker_array['total']+=1
        if worker.state == WorkerStatus.BUSY:
            worker_array['busy']+=1
        if worker.state == WorkerStatus.IDLE:
            worker_array['idle']+=1
    return worker_array

def event_stream():
    r = Redis.from_url(app.config['REDIS_URL'], charset='utf-8', decode_responses=True)
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe('error')
    for message in pubsub.listen():
        yield 'data: %s\n\n' % message['data']