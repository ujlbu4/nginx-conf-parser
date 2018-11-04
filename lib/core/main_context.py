# coding=utf-8
import re


class MainContext:
    daemon = 'on'
    debug_points = None
    env = []
    error_log = dict(file='logs/error.log', level='error')
    load_module = None
    lock_file = 'logs/nginx.lock'
    master_process = 'on'
    pcre_jit = 'off'
    pid = 'logs/nginx.pid'
    ssl_engine = None
    thread_pool = dict(name='default', threads=32, max_queue=65536)
    timer_resolution = None
    working_directory = None
    user = dict(user='nobody', group='nobody')
    worker_cpu_affinity = None
    worker_priority = 0
    worker_processes = 1
    worker_rlimit_core = None
    worker_rlimit_nofile = None
    worker_shutdown_timeout = None
    google_perftools_profiles = None

    def load(self, content):
        # daemon
        daemon = re.search(r'daemon\s+(on|off);', content)
        self.daemon = daemon.group(1) if daemon else self.daemon

        # debug_points
        dp = re.search(r'debug_points\s+(stop|abort);', content)
        self.debug_points = dp.group(1) if dp else self.debug_points

        # env
        env = re.findall(r'env\s+([a-zA-Z0-9=_]+);', content)
        self.env = env

        # error_log
        error_log = re.search(
            r'error_log\s+(([a-zA-Z0-9./\\\-]+)(\s+)?(debug|info|notice|warn|error|crit|alert|emerg)?);', content)
        if error_log:
            self.error_log['file'] = error_log.group(2)
            self.error_log['level'] = error_log.group(4) if error_log.group(4) else 'error'

        # load_module
        load_module = re.search(r'load_module\s+([a-zA-Z0-9\\/.\s]+);', content)
        self.load_module = load_module.group(1) if load_module else self.load_module

        # lock_file
        lock_file = re.search(r'lock_file\s+([a-zA-Z0-9\\/.\s\-]+);', content)
        self.lock_file = lock_file.group(1) if lock_file else self.lock_file

        # master_process
        master_process = re.search(r'master_process\s+(on|off);', content)
        self.master_process = master_process.group(1) if master_process else self.master_process

        # pcre_jit
        pcre = re.search(r'pcre_jit\s+(on|off);', content)
        self.pcre_jit = pcre.group(1) if pcre else self.pcre_jit

        # pid
        pid = re.search(r'pid\s+([a-zA-Z0-9\\/.\s\-]+);', content)
        self.pid = pid.group(1) if pid else self.pid

        # ssl_engine
        engine = re.search(r'ssl_engine\s+([a-zA-Z0-9\\/.\s\-]+);', content)
        self.ssl_engine = engine.group(1) if engine else self.ssl_engine

        # thread_pool
        pool = re.search(r'thread_pool\s+(([a-zA-Z0-9]+)\s+threads=([0-9]+)[\s+]?(max_queue=)?([0-9]+)?);', content)
        if pool:
            self.thread_pool['name'] = pool.group(2)
            self.thread_pool['threads'] = int(pool.group(3))
            self.thread_pool['max_queue'] = int(pool.group(5)) if pool.group(5) else self.thread_pool.get('max_queue')

        # timer_resolution
        timer = re.search(r'timer_resolution\s+([0-9a-zA-Z]+);', content)
        self.timer_resolution = timer.group(1) if timer else self.timer_resolution

        # working_directory
        directory = re.search(r'working_directory\s+([a-zA-Z0-9/.\\_-]+);', content)
        self.working_directory = directory.group(1) if directory else self.working_directory

        # user
        user = re.search(r'user\s+([a-zA-Z0-9_\-]+)(\s+)?([a-zA-Z0-9_\-]+)?;', content)
        if user:
            self.user['user'] = user.group(1)
            self.user['group'] = user.group(3) if user.group(3) else user.group(1)

        # worker_cpu_affinity
        affinity = re.search(r'worker_cpu_affinity\s+([0-9a-zA-Z\s]+);', content)
        self.worker_cpu_affinity = affinity.group(1) if affinity else self.worker_cpu_affinity

        # worker_priority
        priority = re.search(r'worker_priority\s+([0-9]+);', content)
        self.worker_priority = int(priority.group(1)) if priority else self.worker_priority

        # worker_processes
        processes = re.search(r'worker_processes\s+([0-9]+);', content)
        self.worker_processes = int(processes.group(1)) if processes else self.worker_processes

        # worker_rlimit_core
        rlimit_core = re.search(r'worker_rlimit_core\s+([0-9a-zA-Z]+);', content)
        self.worker_rlimit_core = rlimit_core.group(1) if rlimit_core else self.worker_rlimit_core

        # worker_rlimit_nofile
        rlimit_nofile = re.search(r'worker_rlimit_nofile\s+([0-9]+);', content)
        self.worker_rlimit_nofile = int(rlimit_nofile.group(1)) if rlimit_nofile else self.worker_rlimit_nofile

        # worker_shutdown_timeout
        timemout = re.search(r'worker_shutdown_timeout\s+([a-zA-Z0-9]+);', content)
        self.worker_shutdown_timeout = timemout.group(1) if timemout else self.worker_shutdown_timeout

        # google_perftools_profiles
        pertools = re.search(r'google_perftools_profiles\s+([a-zA-Z0-9_.\-\\/]+);', content)
        self.google_perftools_profiles = pertools.group(1) if pertools else self.google_perftools_profiles
