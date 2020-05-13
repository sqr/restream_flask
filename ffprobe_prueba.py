import ffmpeg
import youtube_dl
import json


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

peine = probe('https://cph-msl.akamaized.net/hls/live/2000341/test/master.m3u8')
stream_server = 'rtmp://ie.pscp.tv:80/x/m9b5634x9jwa'
print(peine)
print(get_video_stream(peine))
print(get_audio_stream(peine))

def restream(origin, server):
    
    try:
        stream_map = None
        stream1 = ffmpeg.input(origin)
        stream2 = ffmpeg.input('mosca_66.png')
        probe_decoded = probe(origin)
        video_stream = get_video_stream(probe_decoded)
        audio_stream = get_audio_stream(probe_decoded)
        stream_ol = ffmpeg.overlay(stream1[str(video_stream[0])], stream2, x='main_w-overlay_w-50', y='50')
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
        stream1_audio = stream1[str(audio_stream)]
        stream = ffmpeg.output(stream_ol, stream1_audio, server, format='flv', vcodec='libx264', acodec='aac', preset='veryfast', g='50', threads='2', s='1280x720', crf='23', maxrate='4M', bufsize='5M', channel_layout='stereo')
        ffmpeg.run(stream)
    except:
        print('ERROR') 

origin = 'https://cph-msl.akamaized.net/hls/live/2000341/test/master.m3u8'
restream(origin, stream_server)