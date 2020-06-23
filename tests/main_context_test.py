# coding=utf-8
import unittest

from parser.nginx_conf_parser import MainContext


class MainContextTest(unittest.TestCase):
    def setUp(self):
        self.context = MainContext()

    def test_daemon_extraction(self):
        self.assertEqual('on', self.context.daemon)

        self.context.load("daemon off;")
        self.assertEqual('off', self.context.daemon)

    def test_debug_points_extraction(self):
        self.assertIsNone(self.context.debug_points)

        self.context.load("debug_points abort;")
        self.assertEqual('abort', self.context.debug_points)

    def test_env_extraction(self):
        self.assertEqual(self.context.env, [])

        self.context.load("env NODE_ENV;")
        self.assertEqual(['NODE_ENV'], self.context.env)

        self.context.load("env NODE_ENV=prod; env MALLOC_OPTIONS;")
        self.assertEqual(2, len(self.context.env))
        self.assertIn('NODE_ENV=prod', self.context.env)
        self.assertIn('MALLOC_OPTIONS', self.context.env)

    def test_error_log_extraction(self):
        self.assertEqual(dict(file='logs/error.log', level='error'), self.context.error_log)

        self.context.load("error_log logs/error.log;")
        self.assertEqual(dict(file='logs/error.log', level='error'), self.context.error_log)

        self.context.load("error_log logs/errors.log warn;")
        self.assertEqual(dict(file='logs/errors.log', level='warn'), self.context.error_log)

    def test_load_module_extraction(self):
        self.assertIsNone(self.context.load_module)

        self.context.load("load_module logs/module/to/load;")
        self.assertEqual('logs/module/to/load', self.context.load_module)

    def test_lock_file_extraction(self):
        self.assertEqual('logs/nginx.lock', self.context.lock_file)

        self.context.load("lock_file nginx/lock.lock;")
        self.assertEqual('nginx/lock.lock', self.context.lock_file)

    def test_master_process_extraction(self):
        self.assertEqual('on', self.context.master_process)

        self.context.load('master_process off;')
        self.assertEqual('off', self.context.master_process)

    def test_pcre_jit_extraction(self):
        self.assertEqual('off', self.context.pcre_jit)

        self.context.load('pcre_jit on;')
        self.assertEqual('on', self.context.pcre_jit)

    def test_pid_extraction(self):
        self.assertEqual('logs/nginx.pid', self.context.pid)

        self.context.load('pid /some/file.pid;')
        self.assertEqual('/some/file.pid', self.context.pid)

    def test_ssl_engine_extraction(self):
        self.assertIsNone(self.context.ssl_engine)

        self.context.load('ssl_engine /dev/sda5;')
        self.assertEqual('/dev/sda5', self.context.ssl_engine)

    def test_thread_pool_extraction(self):
        self.assertEqual(dict(name='default', threads=32, max_queue=65536), self.context.thread_pool)

        self.context.load('thread_pool threadPool1 threads=6;')
        self.assertEqual(dict(name='threadPool1', threads=6, max_queue=65536), self.context.thread_pool)

        self.context.load('thread_pool threadPool1 threads=5 max_queue=65432;')
        self.assertEqual(dict(name='threadPool1', threads=5, max_queue=65432), self.context.thread_pool)

    def test_timer_resolution_extraction(self):
        self.assertIsNone(self.context.timer_resolution)

        self.context.load('timer_resolution 100ms;')
        self.assertEqual('100ms', self.context.timer_resolution)

    def test_working_directory_extraction(self):
        self.assertIsNone(self.context.working_directory)

        self.context.load('working_directory /home/user/directory;')
        self.assertEqual('/home/user/directory', self.context.working_directory)

    def test_user_extraction(self):
        self.assertEqual(dict(user='nobody', group='nobody'), self.context.user)

        self.context.load('user user1 user1group;')
        self.assertEqual(dict(user='user1', group='user1group'), self.context.user)

        self.context.load('user user1;')
        self.assertEqual(dict(user='user1', group='user1'), self.context.user)

    def test_worker_cpu_affinity_extraction(self):
        self.assertIsNone(self.context.worker_cpu_affinity)

        self.context.load('worker_cpu_affinity 0001 0010 0100 1000;')
        self.assertEqual('0001 0010 0100 1000', self.context.worker_cpu_affinity)

        self.context.load('worker_cpu_affinity auto 0001 0010 0100 1000;')
        self.assertEqual('auto 0001 0010 0100 1000', self.context.worker_cpu_affinity)

    def test_worker_priority_extraction(self):
        self.assertEqual(0, self.context.worker_priority)

        self.context.load('worker_priority 14;')
        self.assertEqual(14, self.context.worker_priority)

    def test_worker_processes_extraction(self):
        self.assertEqual(1, self.context.worker_processes)

        self.context.load('worker_processes 18;')
        self.assertEqual(18, self.context.worker_processes)

    def test_worker_rlimit_core_extraction(self):
        self.assertIsNone(self.context.worker_rlimit_core)

        self.context.load('worker_rlimit_core 100Mo;')
        self.assertEqual('100Mo', self.context.worker_rlimit_core)

    def test_worker_rlimit_nofile_extraction(self):
        self.assertIsNone(self.context.worker_rlimit_nofile)

        self.context.load('worker_rlimit_nofile 125;')
        self.assertEqual(125, self.context.worker_rlimit_nofile)

    def test_worker_shutdown_timeout_extraction(self):
        self.assertIsNone(self.context.worker_shutdown_timeout)

        self.context.load('worker_shutdown_timeout 100ms;')
        self.assertEqual('100ms', self.context.worker_shutdown_timeout)

    def test_google_perftools_profiles_extraction(self):
        self.assertIsNone(self.context.google_perftools_profiles)

        self.context.load('google_perftools_profiles /some/file;')
        self.assertEqual('/some/file', self.context.google_perftools_profiles)


if __name__ == '__main__':
    unittest.main()
