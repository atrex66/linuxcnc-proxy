
import socket
import threading
import json
import os
import time

DISCOVERY_PORT = 5009
DISCOVERY_MAGIC = b'LINUXCNC_DISCOVER'
DISCOVERY_REPLY_MAGIC = b'LINUXCNC_HERE'

def autodiscover_host(timeout=2.0):
    env_host = os.environ.get('LINUXCNC_HOST')
    if env_host:
        return env_host
    # UDP broadcast discovery
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.settimeout(timeout)
    try:
        s.sendto(DISCOVERY_MAGIC, ('<broadcast>', DISCOVERY_PORT))
        while True:
            try:
                data, addr = s.recvfrom(1024)
                if data.startswith(DISCOVERY_REPLY_MAGIC):
                    return addr[0]
            except socket.timeout:
                break
    finally:
        s.close()
    raise RuntimeError('Could not autodiscover LinuxCNC proxy host')


class stat:
    """
    Mimics linuxcnc.stat() but communicates with the remote proxy.
    """
    def __init__(self, host=None, port=5000):
        if host is None:
            host = autodiscover_host()
        self.host = host
        self.port = port
        self._status = {}
        self._stop = False
        self._thread = threading.Thread(target=self._poll_status, daemon=True)
        self._thread.start()

    def _poll_status(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            while not self._stop:
                try:
                    data = s.recv(4096)
                    if not data:
                        break
                    # Expecting a dict-like string
                    self._status = eval(data.decode().strip())
                except Exception:
                    break

    def poll(self):
        """Update status from remote."""
        # No-op, status is updated in background
        pass

    def __getattr__(self, item):
        return self._status.get(item, None)

    def close(self):
        self._stop = True
