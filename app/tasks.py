from app import app, db
from rq import get_current_job
from app.models import Task, Streaming
import time
import ffmpeg
import youtube_dl
from pathlib import Path
import json

def get_manifest(video_url):
    ydl_opts = {
        'format': 'best'
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        peine = ydl.extract_info(video_url, download=False)

    return peine.get('url')

def generate_url(server, stream_key):
    return server + "/" + stream_key

def convert_reuters(origin):
    return str(Path(origin).parent / 'chunklist_b4096000.m3u8')


def restream(origin, server, stream_key):
    if 'youtu' in origin:
        origin = get_manifest(origin)
    elif 'smil' in origin:
        origin = convert_reuters(origin)
    stream_server = generate_url(server, stream_key)
    try:
        stream_map = None
        stream1 = ffmpeg.input(origin)
        stream2 = ffmpeg.input('mosca_66.png')
        probe_decoded = probe(origin)
        video_stream = get_video_stream(probe_decoded)
        audio_stream = get_audio_stream(probe_decoded)
        stream_ol = ffmpeg.overlay(stream1[video_stream[0]], stream2, x='main_w-overlay_w-50', y='50')
        stream_ol = ffmpeg.filter(stream_ol, 'fps', fps=25, round='up')
        a1 = stream1.audio
        """
        if 'smil' in origin:
            stream1_audio = stream1['2']
        elif 'googlevideo' in origin:
            stream1_audio = a1
        else:
            stream1_audio = stream1['1']
        """
        stream1_audio = stream1[audio_stream]
        if 'dailymotion' in server:
            stream = ffmpeg.output(stream_ol, stream1_audio, stream_server, format='flv', vcodec='libx264', acodec='aac', preset='veryfast', g='50', threads='2', s='1920x1080', crf='23', maxrate='4M', bufsize='5M', channel_layout='stereo')
        else:
            stream = ffmpeg.output(stream_ol, stream1_audio, stream_server, format='flv', vcodec='libx264', acodec='aac', preset='veryfast', g='50', threads='2', s='1280x720', crf='23', maxrate='4M', bufsize='5M', channel_layout='stereo')
        ffmpeg.run(stream)
        set_complete()
    except:
        set_complete() 

def set_complete():
    job = get_current_job()
    if job:
        task = Streaming.query.filter_by(job_id=job.get_id()).first()
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
            if int(streams['tags']['variant_bitrate']) >= audio_bitrate:
                audio_stream = streams['index']
    return audio_stream