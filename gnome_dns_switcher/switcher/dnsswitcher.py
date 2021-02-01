from typing import List

from gnome_dns_switcher.gnome_helpers import Indicator, Connection, async_call
# from gnome_dns_switcher.gnome_helpers import Indicator, Connection, async_call
from .server import Server


class DnsSwitcher(Indicator):
    connections: List[Connection]
    servers: List[Server]

    def __init__(self, application_id: str, servers: List[Server], connections: List[Connection]):
        self.connections = connections
        self.servers = servers
        super().__init__(application_id)

    def init_indicator(self):
        indicator_label = None

        if len(self.connections) < 1:
            self.notify('DNS Switcher', 'No connections found!', 'error')
        else:
            for conn in self.connections:
                self.add_menu_item(f'{conn.name} ({conn.device})')

                for server in self.servers:
                    if ''.join(server.ips) == ''.join(conn.get_dns()):
                        indicator_label = server.name

                    self.add_menu_item(' - ' + server.name, self.switch_dns, conn, server)

            if len(self.connections) > 1:
                indicator_label = 'Multiple connections'

        if not indicator_label:
            indicator_label = '???'

        self.indicator.set_label(indicator_label, indicator_label)

        self.add_menu_item('Debug', self.debug)

    def debug(self):
        pass

    def switch_dns(self, conn: Connection, server: Server):
        print('switching to: ' + server.name + '(' + ', '.join(server.ips) + ')')
        self.indicator.set_label('...', '...')

        async_call(
            lambda: conn.set_dns(server.ips),
            lambda r, e: self.dns_set_complete(conn, server)
        )

    def dns_set_complete(self, conn: Connection, server: Server):
        result_dns = ', '.join(conn.get_dns())
        if result_dns != ', '.join(server.ips):
            self.notify("DNS Switcher", "Error switching, result doesn't match. Result: " + result_dns, 'error')
        else:
            self.indicator.set_label(server.name, server.name)
            self.notify("DNS Switcher", f"Switched server to: [{server.name}] {result_dns}", 'network-wired')
