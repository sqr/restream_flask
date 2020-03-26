from redis import Redis
import rq

queue = rq.Queue('microblog-tasks', connection=Redis.from_url('redis://:PeinesitoPeinador2020$@sqrsrv.no-ip.org:6379/0'))
job = queue.enqueue('app.ffmpegtasks.ffmpegtask', job_timeout='1h', description='test stream')