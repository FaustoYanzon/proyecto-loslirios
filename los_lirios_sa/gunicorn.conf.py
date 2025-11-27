# Configuración de Gunicorn para Los Lirios SA

import multiprocessing
import os

# === CONFIGURACIÓN DEL SERVIDOR ===
bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100

# === CONFIGURACIÓN DE PROCESOS ===
preload_app = True
keepalive = 5
timeout = 30
graceful_timeout = 30

# === LOGGING ===
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# === SEGURIDAD ===
user = "www-data"
group = "www-data"
tmp_upload_dir = None

# === CONFIGURACIÓN DE DJANGO ===
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'los_lirios_sa.settings')

def when_ready(server):
    server.log.info("Servidor Gunicorn listo para Los Lirios SA")

def worker_int(worker):
    worker.log.info("Worker recibió INT o QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    worker.log.info("Worker received SIGABRT signal")