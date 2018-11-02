# coding=utf-8
from core.context import Context


class MainContext(Context):
    def __init__(self, content):
        super().__init__(content)

    def _parse(self):
        super(MainContext, self)._parse()

        super(MainContext, self)._extract_values('daemon', 'on')
        super(MainContext, self)._extract_values('debug_points', None)
        super(MainContext, self)._extract_values('env', 'TZ')
        super(MainContext, self)._extract_values('error_log', 'logs/error.log error')
        super(MainContext, self)._extract_values('load_module', None)
        super(MainContext, self)._extract_values('lock_file', 'logs/nginx.lock')
        super(MainContext, self)._extract_values('master_process', 'on')
        super(MainContext, self)._extract_values('pcre_jit', 'off')
        super(MainContext, self)._extract_values('pid', 'logs/nginx.pid')
        super(MainContext, self)._extract_values('ssl_engine', None)
        super(MainContext, self)._extract_values('thread_pool', 'default threads=32 max_queue=65536')
        super(MainContext, self)._extract_values('timer_resolution', None)
        super(MainContext, self)._extract_values('working_directory', None)
        super(MainContext, self)._extract_values('user', 'nobody nobody')
        super(MainContext, self)._extract_values('worker_cpu_affinity', None)
        super(MainContext, self)._extract_values('worker_priority', '0')
        super(MainContext, self)._extract_values('worker_processes', '1')
        super(MainContext, self)._extract_values('worker_rlimit_core', None)
        super(MainContext, self)._extract_values('worker_rlimit_nofile', None)
        super(MainContext, self)._extract_values('worker_shutdown_timeout', None)
        super(MainContext, self)._extract_values('google_perftools_profiles', None)

