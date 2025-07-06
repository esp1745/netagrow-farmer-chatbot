# Gunicorn configuration file for production deployment
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "netagrow-chatbot"

# Server mechanics
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (if using SSL termination at nginx level, keep False)
keyfile = None
certfile = None

# Preload app for better performance
preload_app = True

# Worker timeout
graceful_timeout = 30

# Environment variables
raw_env = [
    "FLASK_ENV=production",
]

def when_ready(server):
    """Log when server is ready"""
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    """Log when worker receives SIGINT"""
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Log before forking"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """Log after forking"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    """Log after worker initialization"""
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    """Log when worker aborts"""
    worker.log.info("Worker aborted (pid: %s)", worker.pid) 