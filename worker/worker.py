import redis
from rq import Queue, Worker

redis_conn = redis.Redis(host="redis", port=6379)

if __name__ == "__main__":
    worker = Worker([Queue("default", connection=redis_conn)])
    worker.work()