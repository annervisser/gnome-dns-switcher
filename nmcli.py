import subprocess
from typing import NamedTuple, List


class Connection(NamedTuple):
    name: str
    uuid: str
    type: str
    device: str

    def get_dns(self) -> List[str]:
        output = run_command('nmcli --get-values ip4.dns connection show {}'.format(self.uuid), False)
        return output.split(' | ')

    def set_dns(self, dns: List[str], reload=True):
        run_command('nmcli connection modify {} ipv4.dns "{}"'.format(self.uuid, ','.join(dns)), False)
        if reload:
            self.reload_connection()

    def reload_connection(self):
        run_command('nmcli connection up {}'.format(self.uuid), False)


def run_command(command: str, split_lines=True):
    cmd = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output = cmd.stdout.read().decode('utf8').strip('\n')
    return output.split('\n') if split_lines else output


def get_connections() -> List[Connection]:
    output = run_command('nmcli --terse connection show --active')
    connections: List[Connection] = [Connection(*line.split(':')) for line in output]
    return [conn for conn in connections if conn.type not in ['bridge']]
