import subprocess
from typing import NamedTuple, List


class Connection(NamedTuple):
    name: str
    uuid: str
    type: str
    device: str

    def get_dns(self) -> List[str]:
        output = run_command('nmcli --get-values ip4.dns connection show {}'.format(self.uuid))
        return output.split(' | ')

    def set_dns(self, dns: List[str]):
        run_command('nmcli connection modify {} ipv4.dns "{}"'.format(self.uuid, ','.join(dns)))

    def get_dns_auto_mode(self):
        output = run_command('nmcli --get-values ipv4.ignore-auto-dns connection show {}'.format(self.uuid))
        output = output.strip().lower()
        # Invert cause it's ignore
        if output == 'yes':
            return False
        elif output == 'no':
            return True
        raise Exception('Invalid return value from dns auto mode')

    def set_dns_auto_mode(self, auto: bool):
        run_command('nmcli connection modify {} ipv4.ignore-auto-dns {}'
                    .format(self.uuid, 'no' if auto else 'yes'))  # invert cause its ignore

    def reload_connection(self):
        run_command('nmcli connection up {}'.format(self.uuid))

    def reload_dns(self):
        """
        This is a clean way to reload DNS, but it requires root privileges
        """
        run_command('nmcli general reload dns-full {}'.format(self.uuid))


def run_command(command: str, split_lines=False) -> str:
    cmd = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output = cmd.stdout.read().decode('utf8').strip('\n')
    return output.split('\n') if split_lines else output


def get_connections() -> List[Connection]:
    output = run_command('nmcli --terse connection show --active', True)
    connections: List[Connection] = [Connection(*line.split(':')) for line in output]
    return [conn for conn in connections if conn.type not in ['bridge']]
