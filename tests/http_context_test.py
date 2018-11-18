# coding=utf-8
import unittest
from nginx_conf_parser.http_context import HttpContext


class HttpContextTest(unittest.TestCase):
    def setUp(self):
        self.context_string = """
        http {
            absolute_redirect off; 
            
            location /user/ {
                absolute_redirect on;
                proxy_pass http://user.example.com;
            }

            location = /user {
                absolute_redirect on;
                proxy_pass http://login.example.com;
            }
            
            server {
                absolute_redirect on;
                location = /test {
                    absolute_redirect on;
                    proxy_pass http://login.example2.com; 
                } 
            }
            
            server {
                absolute_redirect on;
                location = /test2 {
                    absolute_redirect on;
                    proxy_pass http://login.example3.com; 
                }
            }
        }
        """
        self.http = HttpContext(self.context_string)

    def test_servers_extraction(self):
        pass

if __name__ == '__main__':
    unittest.main()
