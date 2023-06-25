import time
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
                    if server.ips and ''.join(server.ips) == ''.join(conn.get_dns()):
                        indicator_label = server.name

                    self.add_menu_item(' - ' + server.name, self.switch_dns, conn, server)

                self.add_separator()

                if conn.get_dns_auto_mode():
                    indicator_label = 'DHCP'

            if len(self.connections) > 1:
                indicator_label = 'Multiple connections'

        if not indicator_label:
            indicator_label = '???'

        self.set_label(indicator_label)

        self.add_separator()
        self.add_menu_item('Reload', self.reload)
        self.add_menu_item('Restart NW Manager', self.restart_nw_manager)

    def restart_nw_manager(self):
        from gnome_dns_switcher.gnome_helpers.nmcli import run_command
        self.set_label('Restarting...')

        def reload_call():
            run_command('systemctl restart NetworkManager')
            self.set_label('Reloading...')
            time.sleep(5)

        async_call(
            reload_call,
            lambda r, e: self.reload()
        )

    def reload(self):
        self.close(42)

    def switch_dns(self, conn: Connection, server: Server):
        self.set_label('...')

        def set_call():
            if server.dhcp:
                conn.set_dns([])
                conn.set_dns_auto_mode(True)
                conn.reload_connection()
            else:
                conn.set_dns(server.ips)
                conn.set_dns_auto_mode(False)
                conn.reload_connection()

        async_call(
            set_call,
            lambda r, e: self.dns_set_complete(conn, server)
        )

    def dns_set_complete(self, conn: Connection, server: Server = None):
        result_dns_ips = ', '.join(conn.get_dns())
        result_dhcp = conn.get_dns_auto_mode()

        if server.dhcp != result_dhcp:
            self.notify(
                "DNS Switcher",
                "Error switching, DHCP status doesn't match. Result: " + str(result_dhcp),
                "error"
            )
        elif not server.dhcp and result_dns_ips != ', '.join(server.ips):
            self.notify("DNS Switcher", "Error switching, result doesn't match. Result: " + result_dns_ips, 'error')
        else:
            label = server.name
            if len(self.connections) > 1:
                label = "{0}: {1}".format(conn.name, label)
            self.set_label(label)
            self.notify("DNS Switcher", f"Switched server to: [{server.name}] {result_dns_ips}", 'network-wired')
