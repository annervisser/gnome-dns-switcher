import argparse
import os
from os.path import isfile
from typing import List

import yaml

from .gnome_helpers import get_connections
from .switcher import Server, DnsSwitcher

CONFIG_PATH = os.path.expanduser("~/.config/gnome-dns-switcher.yml")

APPINDICATOR_ID = 'gnome_dns_switcher'

# language=yaml
DEFAULT_CONFIG = '''
servers:
  # DHCP is always shown as the first option
  Quad9: 9.9.9.9
  CloudFlare: [1.1.1.1, 1.0.0.1]
  Google DNS:
    - 8.8.8.8
    - 8.8.4.4
devices: [] # Specify device names here if you want to hide certain devices (ip link show)
'''


def main():
    parser = argparse.ArgumentParser(description='Gnome Dns Switcher')
    subcommands = parser.add_subparsers()
    parser.set_defaults(subcommand=None)

    parser.add_argument(
        "--config",
        dest="config",
        required=False,
        default=CONFIG_PATH,
        help="Path to config yaml",
        metavar="FILE",
    )

    generate_config_command = subcommands.add_parser(
        'generate-config',
        help=f'Generate an example configuration file in {CONFIG_PATH}'
    )
    generate_config_command.set_defaults(subcommand='generate-config')

    args = parser.parse_args()
    config_path = os.path.expanduser(args.config)

    if args.subcommand == 'generate-config':
        if isfile(config_path):
            print(f'A file already exists at {config_path}')
            exit(1)
        print(f'Generating config at {config_path}')
        os.umask(0o077)
        os.makedirs(os.path.dirname(config_path), 0o700, exist_ok=True)
        with open(config_path, 'x') as config_file:
            config_file.write(DEFAULT_CONFIG)
        print(f'Config file written!')
        if (config_path != CONFIG_PATH):
            print(f'To use this config file, run this program with --config {config_path}')
        exit(0)

    result = 42  # 42 === reload
    while result == 42:
        connections, servers = load_config(config_path)
        menu = DnsSwitcher(APPINDICATOR_ID, servers, connections)
        result = menu.open()

    print("Done")


def load_config(config_path):
    if not isfile(config_path):
        print(
            f"There is no file at the specified config path ({config_path}).\n"
            f"Create it by running `gnome-dns-switcher generate-config` or specify a different path with --config"
        )
        exit(1)

    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file)
        servers: List[Server] = [Server('DHCP', None, True)]
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
        filter_by_names = config.get('devices') or []
        if len(filter_by_names):
            connections = [c for c in connections if c.device in filter_by_names]
    return connections, servers


if __name__ == "__main__":
    main()
