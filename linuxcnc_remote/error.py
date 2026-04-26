
import socket
import threading
import json
import os
from .stat import autodiscover_host


class error:
    """
    Mimics linuxcnc error channel, receives error messages from the remote proxy.
    """
    def __init__(self, host=None, port=5002):
        if host is None:
            host = autodiscover_host()
        self.host = host
        self.port = port
        self._error = None
        self._stop = False
        self._thread = threading.Thread(target=self._poll_error, daemon=True)
        self._thread.start()

    def _poll_error(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            while not self._stop:
                try:
                    data = s.recv(4096)
                    if not data:
                        break
                    msg = json.loads(data.decode().strip())
                    self._error = msg.get("error", None)
                except Exception:
                    break

    def poll(self):
        """Update error from remote."""
        # No-op, error is updated in background
        pass

    def get(self):
        return self._error

    def close(self):
        self._stop = True
