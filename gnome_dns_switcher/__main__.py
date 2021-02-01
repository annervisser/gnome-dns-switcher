from os.path import isfile
from typing import List

import yaml

from gnome_dns_switcher.gnome_helpers import get_connections
from gnome_dns_switcher.switcher import Server, DnsSwitcher

APPINDICATOR_ID = 'dns_switcher'


def main():
    config_file = 'config.yml'
    if not isfile(config_file):
        print('File config.yml not found. Please create it and run again.')
        exit(1)

    with open('config.yml', 'r') as config_file:
        config = yaml.safe_load(config_file)
        servers: List[Server] = []
        for name, ips in config.get('servers', {}).items():
            if not name or not ips:
                continue

            if isinstance(ips, str):
                ips = ips.split(',')

            # Remove all whitespace
            ips = [''.join(ip.split()) for ip in ips if ip]
            if len(ips):
                server = Server(name.strip(), ips)
                servers.append(server)

        connections = get_connections()
        filter_by_names = config.get('devices', [])
        if len(filter_by_names):
            connections = [c for c in connections if c.device in filter_by_names]

    DnsSwitcher(APPINDICATOR_ID, servers, connections)


if __name__ == "__main__":
    main()
