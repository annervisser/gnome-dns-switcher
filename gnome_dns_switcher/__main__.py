import argparse
from os.path import isfile
from typing import List

import yaml

from gnome_helpers import get_connections
from switcher import Server, DnsSwitcher

APPINDICATOR_ID = 'gnome_dns_switcher'


def main():
    parser = argparse.ArgumentParser(description='Gnome Dns Switcher')
    parser.add_argument("--config", dest="config", required=False, default="./config.yml",
                        help="Path to config yaml", metavar="FILE",
                        type=lambda x:
                        x if isfile(x)
                        else parser.error("Specified config file ({}) is not a file. "
                                          "Create it or specify a different path with --config".format(x)))

    args = parser.parse_args()

    with open(args.config, 'r') as config_file:
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
