
import socket
import json
import os
from .stat import autodiscover_host


class command:
    """
    Mimics linuxcnc.command() but communicates with the remote proxy.
    """
    def __init__(self, host=None, port=5001):
        if host is None:
            host = autodiscover_host()
        self.host = host
        self.port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((self.host, self.port))

    def __getattr__(self, item):
        def remote_command(*args, **kwargs):
            cmd = {"cmd": item, "args": args, "kwargs": kwargs}
            self._sock.sendall((json.dumps(cmd) + '\n').encode())
            data = self._sock.recv(4096)
            if not data:
                raise RuntimeError("Lost connection to proxy")
            result = json.loads(data.decode().strip())
            return result.get("result", None)
        return remote_command

    def close(self):
        self._sock.close()
