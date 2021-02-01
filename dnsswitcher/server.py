from typing import NamedTuple, List


class Server(NamedTuple):
    name: str
    ips: List[str]

    def __str__(self):
        return self.name + ': ' + ', '.join(self.ips)
