import argparse
import os
import re
from typing import List

import requests
import pandas as pd
from pyhocon import ConfigFactory, ConfigTree
from tabulate import tabulate

from services_spec_generator.nginx_conf_parser.http_context import HttpContext
from services_spec_generator.nginx_config_merge import NginxMergedDumper


dir_path = os.path.dirname(os.path.realpath(__file__))

config = ConfigTree(
    ConfigFactory.parse_file(f'{dir_path}/config.conf')
)


def get_hosts_ips(bind_zones_file_location):
    map_ips = {}  # {'192.168.0.1': ['example.com', 'work.example.com']}
    map_hosts = {}  # {'exmaple.com': '192.168.1.1'}

    with open(bind_zones_file_location, 'r', encoding='utf-8') as file:
        for line in file:

            # for parse such record: d-1cdb1      IN      A      10.69.0.241
            zone_record = re.search(r'([^\s;]*)\s+IN\s+A\s+([\d\.]+)', line)
            host = zone_record.group(1) if zone_record else None
            ip = zone_record.group(2) if zone_record else None

            if host is not None:
                map_hosts[host] = ip
                if ip in map_ips:
                    map_ips[ip].append(host)
                else:
                    map_ips[ip] = [host]

    print('map_ips\n', map_ips)
    print('map_hosts\n', map_hosts)
    print()
    return map_ips, map_hosts


def define_stand_by_host(host):
    if 'work' in host:
        return 'work'

    if 'stage' in host:
        return 'stage'

    if 'prod' in host:
        return 'prod'

    return 'int'


def is_ip(content):
    matched = re.search(r'(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)', content)
    return True if matched else False


def is_host(content):
    matched = re.search(r'[\w-\.]+', content)
    return True if matched else False


git_projects_cache = {}


def get_git_project_details(git_project):
    base_url = f'{config.gitlab_base_url}/projects/'

    default_result = {'name': '', 'web_url': ''}
    if git_project is None:
        return default_result

    def extract_project():
        project = git_project.replace("https://", "")
        project = project.replace("http://", "")
        project = project.replace("gitlab.yourltd.com/", "")
        project = project[:-1] if project[-1] == "/" else project  # remove trailing slash
        return project

    project = extract_project()

    if project in git_projects_cache:
        return git_projects_cache[project]
    else:
        project_encoded = requests.utils.quote(project, safe='')
        response = requests.get(base_url + project_encoded,
                                headers={"Private-Token": config.gitlab_private_token})

        if response.status_code != 200:
            git_projects_cache[project] = default_result
            print(f'WARN: {base_url + project_encoded} returned [{response.status_code}]')
        else:
            print(response.json())
            git_projects_cache[project] = response.json()

        return git_projects_cache[project]


class RowItem:
    def __init__(self, domain, service_name, service_git_url, upstream, stand, host, ip, port, location):
        self.domain = domain
        self.service_name = service_name
        self.service_git_url = service_git_url
        self.upstream = upstream
        self.stand = stand
        self.host = host
        self.ip = ip
        self.port = int(port)
        self.location = location

    def to_list(self):
        return [self.domain, self.service_name, self.service_git_url, self.upstream, self.stand, self.host,
                self.ip, self.port, self.location]

    @staticmethod
    def get_header():
        return ['domain', 'service_name', 'service_git_url', 'upstream', 'stand', 'host', 'ip', 'port', 'location']


class DataTable:
    def __init__(self):
        self.rows: List[RowItem] = []

    def to_list(self):
        return [row.to_list() for row in self.rows]

    def get_headers(self):
        if len(self.rows) > 0:
            return self.rows[0].get_header()
        return []


class IPrintResults:
    @staticmethod
    def format_row(row: RowItem):
        raise NotImplemented()

    @staticmethod
    def print_table(tbl: DataTable):
        raise NotImplemented()


class ConsolePrint(IPrintResults):
    @staticmethod
    def format_row(row: RowItem):
        return [row.domain, row.service_name, row.service_git_url, row.upstream,
                row.stand, row.host, row.ip, row.port, row.location]

    @staticmethod
    def print_table(tbl: DataTable):
        prepared_table = tbl.to_list()
        print(tabulate(prepared_table, headers=tbl.get_headers(), tablefmt='simple'))


class FileCSVPrint(IPrintResults):
    @staticmethod
    def format_row(row: RowItem):
        return f'{row.domain},{row.service_name},{row.service_git_url},{row.upstream},' + \
               f'{row.stand},{row.host},{row.ip},{row.port},{row.location}'

    @staticmethod
    def print_table(tbl: DataTable):
        with open('services_table.csv', 'w', encoding='utf-8') as file:
            file.write('domain,service_name,service_git_url,upstream,stand,host,ip,port,location\n')
            for row in tbl.rows:
                file.write(FileCSVPrint.format_row(row) + '\n')


class HtmlPrint(IPrintResults):
    @staticmethod
    def format_row(row: RowItem):
        pass

    @staticmethod
    def print_table(tbl: DataTable):
        df = pd.DataFrame(tbl.to_list(), columns=['domain', 'service_name', 'service_git_url', 'upstream',
                                                  'stand', 'host', 'ip', 'port', 'location'])

        sorted_grouped_by_tbl = df \
            .sort_values(['port', 'service_name', 'service_git_url', 'stand', 'domain', 'location'], ascending=True) \
            .groupby(['port', 'service_name', 'service_git_url', 'stand', 'domain', 'location'], as_index=True) \
            .count()

        desired_table = sorted_grouped_by_tbl.drop(columns=['upstream', 'host', 'ip'])

        # print(desired_table.to_string())
        html = desired_table.to_html(justify='left')
        with open('services_table.html', 'w') as file:
            file.write(html)


def make_single_nginx_conf(upstreams_conf_file_path,
                           sites_available_conf_files_path):
    nginx_conf_file = './nginx.conf'
    with open(nginx_conf_file, 'w', encoding='utf-8') as nginx_conf_to_resolve:
        nginx_conf_to_resolve.write("http { \n")
        nginx_conf_to_resolve.write(f"\t include {upstreams_conf_file_path};\n")
        nginx_conf_to_resolve.write(f"\t include {sites_available_conf_files_path};\n")
        nginx_conf_to_resolve.write("}")

    # resolve all includes
    conf_file = NginxMergedDumper(nginx_conf_file).as_string()
    return conf_file


def parse_server(upstreams_conf_file_path,
                 sites_available_conf_files_path,
                 bind_zones_file_location):
    conf_file = make_single_nginx_conf(upstreams_conf_file_path, sites_available_conf_files_path)
    parsed_http_context = HttpContext(conf_file)
    map_ips, map_host = get_hosts_ips(bind_zones_file_location)

    result_table = DataTable()
    upstreams_map = {}
    for upstream in parsed_http_context.upstreams:
        upstreams_map[upstream.name] = upstream

    for server in parsed_http_context.servers:
        server_listen_port = server.listen[0]['value']
        for location in server.location:
            if isinstance(server.server_name, list):
                domains = server.server_name
            else:
                domains = [server.server_name]

            for domain in domains:
                if location.proxy_pass is None or location.proxy_pass_upstream is None:  # если proxy_pass нет
                    continue
                upstream_name = location.proxy_pass_upstream

                if upstream_name in upstreams_map.keys():
                    upstream_servers = upstreams_map[upstream_name].servers
                else:
                    upstream_servers = [{'address': upstream_name}]

                location_path = location.path
                for upstream_server in upstream_servers:
                    # print( upstream_server, upstream_name, domain)
                    if ":" in upstream_server['address']:
                        host, port = upstream_server['address'].split(":")
                    else:
                        host = upstream_server['address']
                        port = None

                    if is_ip(host):
                        ip = host
                        hosts = map_ips[ip]
                    else:
                        host = host.replace('.yourltd.com', '')
                        ip = map_host[host]
                        hosts = [host]

                    for host in hosts:
                        stand = define_stand_by_host(host)

                        if upstream_name in upstreams_map.keys():
                            project_details = get_git_project_details(upstreams_map[upstream_name].git_project)

                            row = RowItem(domain=domain,
                                          service_name=project_details["name"],
                                          service_git_url=project_details["web_url"],
                                          upstream=upstream_name,
                                          stand=stand,
                                          host=host,
                                          ip=ip, port=port,
                                          location=location_path)
                            result_table.rows.append(row)

    return result_table


def parse_args():
    ap = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    ap.add_argument('--upstreams_conf_file_path', required=True,
                    help='Upstreams conf file; Examples:\n'
                         "  --upstreams_conf_file_path='./puppet/modules/profile/files/nginx/host_d-ngx1.yourltd.com/conf.d/backends.conf'"
                    )
    ap.add_argument('--sites_available_conf_files_path', required=True,
                    help='Examples:\n'
                         "  --sites_available_conf_files_path='./puppet/modules/profile/files/nginx/host_d-ngx1.yourltd.com/sites-available/*.conf'"
                    )
    ap.add_argument('--bind_zones_file_location', required=True,
                    help='Examples:\n'
                         "  --bind_zones_file_location='./puppet/modules/profile/files/bind9/zones/yourltd.com'"
                    )

    args = ap.parse_args()

    return args


def main():
    args = parse_args()
    services_table = parse_server(upstreams_conf_file_path=args.upstreams_conf_file_path,
                                  sites_available_conf_files_path=args.sites_available_conf_files_path,
                                  bind_zones_file_location=args.bind_zones_file_location)

    # upstreams_conf_file_path='/Users/ujlbu4/Work/yourltd/misc/puppet/modules/profile/files/nginx/host_d-ngx1.yourltd.com/conf.d/backends.conf',
    # sites_available_conf_files_path='/Users/ujlbu4/Work/yourltd/misc/puppet/modules/profile/files/nginx/host_d-ngx1.yourltd.com/sites-available/*.conf',
    # bind_zones_file_location='/Users/ujlbu4/Work/yourltd/misc/puppet/modules/profile/files/bind9/zones/yourltd.com'

    ConsolePrint.print_table(services_table)
    FileCSVPrint.print_table(services_table)
    HtmlPrint.print_table(services_table)


if __name__ == '__main__':
    # get_hosts_ips()
    # get_git_project_details("https://gitlab.yourltd.com/services/suparservice/")
    main()
