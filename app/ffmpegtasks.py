import time
from rq import get_current_job
import ffmpeg
import youtube_dl


def get_manifest(video_url):
        ydl_opts = {
            'format': 'best'
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            peine = ydl.extract_info(video_url, download=False)

        return peine.get('url')

def ffmpegtask():

    VIDEO_URL = 'https://www.youtube.com/watch?v=dp8PhLsUcFE'
    RTMP_SERVER = 'rtmp://publish.dailymotion.com/publish-dm/x745s0j?auth=eIVE_72b5fc183ed5507672cdff8537d47885aead794f'

    stream_map = None
    stream1 = ffmpeg.input(get_manifest(VIDEO_URL), re=None)
    stream2 = ffmpeg.input('mosca_66.png')
    stream_ol = ffmpeg.overlay(stream1, stream2, x='main_w-overlay_w-50', y='50')
    a1 = stream1.audio
    stream = ffmpeg.output(stream_ol, a1, RTMP_SERVER, format='flv', vcodec='libx264', acodec='aac', preset='medium', g='120', crf='23', maxrate='4M', bufsize='5M', channel_layout='stereo')
    subp = ffmpeg.run(stream)

def example(seconds):
    job = get_current_job()
    print('Starting task')
    for i in range(seconds):
        job.meta['progress'] = 100.0 * i / seconds
        job.save_meta()
        print(i)
        time.sleep(1)
    job.meta['progress'] = 100
    job.save_meta()
    print('Task completed')

# start rq worker: rq worker -u 'redis://:PeinesitoPeinador2020$@sqrsrv.no-ip.org:6379/0' microblog-tasks en consola    
# >>> job = queue.enqueue('app.ffmpegtasks.ffmpegtask', job_timeout='12h')