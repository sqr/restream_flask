import ffmpeg
import youtube_dl

def get_manifest(video_url):
    ydl_opts = {
        'format': 'best'
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        peine = ydl.extract_info(video_url, download=False)

    return peine.get('url')

VIDEO_URL = 'https://www.youtube.com/watch?v=dp8PhLsUcFE'
RTMP_SERVER = 'rtmp://a.rtmp.youtube.com/live2/r1mr-8fra-czhb-agqe'

try:
    stream_map = None
    stream1 = ffmpeg.input(get_manifest(VIDEO_URL), re=None)
    stream2 = ffmpeg.input('mosca_65.png')
    stream_ol = ffmpeg.overlay(stream1, stream2, x='main_w-overlay_w-50', y='50')
    a1 = stream1.audio
    stream = ffmpeg.output(stream_ol, a1, RTMP_SERVER, format='flv', vcodec='libx264', acodec='aac', preset='medium', g='120', crf='23', maxrate='4M', bufsize='5M', channel_layout='stereo')
    print(stream.get_args())
    subp = ffmpeg.run(stream, capture_stderr=True)
except ffmpeg.Error as e:
    print('stderr:', e.stderr.decode('utf8'))
    print('peine')        