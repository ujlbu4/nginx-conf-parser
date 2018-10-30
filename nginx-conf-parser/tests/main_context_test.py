# coding=utf-8
import unittest

from core.main_context import MainContext


class MainContextTest(unittest.TestCase):
    def test_default_directive_values_extraction(self):
        main_context = MainContext("")
        self.assertEqual(main_context.daemon, 'on')
        self.assertIsNone(main_context.debug_points)
        self.assertEqual(main_context.env, 'TZ')
        self.assertEqual(main_context.error_log, 'logs/error.log error')
        self.assertIsNone(main_context.load_module)
        self.assertEqual(main_context.lock_file, 'logs/nginx.lock')
        self.assertEqual(main_context.master_process, 'on')
        self.assertEqual(main_context.pcre_jit, 'off')
        self.assertEqual(main_context.pid, 'logs/nginx.pid')
        self.assertIsNone(main_context.ssl_engine)
        self.assertEqual(main_context.thread_pool, 'default threads=32 max_queue=65536')
        self.assertIsNone(main_context.timer_resolution)
        self.assertEqual(main_context.user, 'nobody nobody')
        self.assertIsNone(main_context.worker_cpu_affinity)
        self.assertEqual(main_context.worker_priority, '0')
        self.assertEqual(main_context.worker_processes, '1')
        self.assertIsNone(main_context.worker_rlimit_core)
        self.assertIsNone(main_context.worker_rlimit_nofile)
        self.assertIsNone(main_context.worker_shutdown_timeout)
        self.assertIsNone(main_context.working_directory)

    def test_simple_directive_extraction(self):
        # daemon
        main_context = MainContext("daemon off;")
        self.assertEqual(main_context.daemon, 'off')

        # debug points
        main_context = MainContext("debug_points abort;")
        self.assertEqual(main_context.debug_points, 'abort')
        main_context = MainContext("debug_points stop;")
        self.assertEqual(main_context.debug_points, 'stop')

        # env
        main_context = MainContext("env MALLOC_OPTIONS;")
        self.assertIsInstance(main_context.env, str)
        self.assertEqual(main_context.env, 'MALLOC_OPTIONS')
        main_context = MainContext("env MALLOC_OPTIONS; env PERL5LIB=/data/site/modules;")
        self.assertIsInstance(main_context.env, list)
        self.assertIn('MALLOC_OPTIONS', main_context.env)
        self.assertIn('PERL5LIB=/data/site/modules', main_context.env)

        # error_log
        main_context = MainContext("error_log endpoint/error.log warn;")
        self.assertEqual(main_context.error_log, "endpoint/error.log warn")

        # load_module
        main_context = MainContext("load_module modules/ngx_mail_module.so;")
        self.assertEqual(main_context.load_module, 'modules/ngx_mail_module.so')

        # lock_file
        main_context = MainContext("lock_file some/lock/file.lock;")
        self.assertEqual(main_context.lock_file, "some/lock/file.lock")

        # master_process
        main_context = MainContext("master_process off;")
        self.assertEqual(main_context.master_process, 'off')

        # pcre_jit
        main_context = MainContext("pcre_jit on;")
        self.assertEqual(main_context.pcre_jit, 'on')

        # pid
        main_context = MainContext("pid logs/nginxxxx.pid;")
        self.assertEqual(main_context.pid, "logs/nginxxxx.pid")

        # ssl_engine
        main_context = MainContext("ssl_engine some-device;")
        self.assertEqual(main_context.ssl_engine, 'some-device')

        # thread_pool
        main_context = MainContext("thread_pool default threads=64 max_queue=65000;")
        self.assertEqual(main_context.thread_pool, 'default threads=64 max_queue=65000')

        # timer_resolution
        main_context = MainContext("timer_resolution 100ms;")
        self.assertEqual(main_context.timer_resolution, "100ms")

        # user
        main_context = MainContext("user www-data www-data;")
        self.assertEqual(main_context.user, "www-data www-data")

        # worker_cpu_affinity
        main_context = MainContext("worker_cpu_affinity 0001 0010 0100 1000;")
        self.assertEqual(main_context.worker_cpu_affinity, '0001 0010 0100 1000')

        # worker_priority
        main_context = MainContext("worker_priority 1;")
        self.assertEqual(main_context.worker_priority, '1')

        # worker_processes
        main_context = MainContext("worker_processes 4;")
        self.assertEqual(main_context.worker_processes, '4')

        # worker_rlimit_core
        main_context = MainContext("worker_rlimit_core 12;")
        self.assertEqual(main_context.worker_rlimit_core, '12')

        # worker_rlimit_nofile
        main_context = MainContext("worker_rlimit_nofile 12;")
        self.assertEqual(main_context.worker_rlimit_nofile, '12')

        # worker_shutdown_timeout
        main_context = MainContext("worker_shutdown_timeout 100ms;")
        self.assertEqual(main_context.worker_shutdown_timeout, '100ms')

        # working_directory
        main_context = MainContext("working_directory /home/user;")
        self.assertEqual(main_context.working_directory, '/home/user')


if __name__ == '__main__':
    unittest.main()
