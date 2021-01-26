import async_helpers
from indicator import Indicator
from nmcli import get_connections, Connection

APPINDICATOR_ID = 'anner_dns_switcher'

dns_options = ['1.1.1.1', '8.8.8.8', '8.8.4.4']


class DnsIndicator(Indicator):
    def init_indicator(self):
        connections = get_connections()
        if len(connections) == 1:
            status = ', '.join(connections[0].get_dns())
            self.indicator.set_label(status, status)

        for conn in connections:
            self.add_menu_item(conn.name)

            for dns in dns_options:
                self.add_menu_item(' - ' + dns, self.switch_dns, conn, dns)

    def switch_dns(self, conn: Connection, server: str):
        print('switching to: ' + server)
        self.indicator.set_label('...', '...')

        async_helpers.async_call(
            lambda: conn.set_dns([server]),
            lambda r, e: self.dns_set_complete(conn)
        )

    def dns_set_complete(self, conn):
        print('result: ', conn.get_dns())
        dns_string = ', '.join(conn.get_dns())
        self.indicator.set_label(dns_string, dns_string)
        self.notify("DNS Switcher", "Switched server to: " + dns_string)


if __name__ == "__main__":
    DnsIndicator(APPINDICATOR_ID)
