import socket
import threading
import json
import os

HAL_BIT = 1
HAL_FLOAT = 2
HAL_IN = 1
HAL_OUT = 2

HAL_PORT = 5003

def _get_host():
    return os.environ.get('LINUXCNC_HOST', '127.0.0.1')

class component:
    def __init__(self, name, host=None, port=HAL_PORT):
        self.name = name
        self.host = host or _get_host()
        self.port = port
        self._pins = {}
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((self.host, self.port))
        self._lock = threading.Lock()
        self._listener = threading.Thread(target=self._listen, daemon=True)
        self._listener.start()
        self._ready = False

    def newpin(self, name, ptype, direction):
        ptype_str = 'bit' if ptype == HAL_BIT else 'float'
        dir_str = 'in' if direction == HAL_IN else 'out'
        msg = {"action": "create_pin", "name": name, "type": ptype_str, "dir": dir_str}
        self._send(msg)
        self._pins[name] = None

    def ready(self):
        self._send({"action": "ready"})
        self._ready = True

    def __setitem__(self, name, value):
        self._send({"action": "set_pin", "name": name, "value": value})
        self._pins[name] = value

    def __getitem__(self, name):
        self._send({"action": "get_pin", "name": name})
        # Wait for update
        for _ in range(10):
            if self._pins.get(name) is not None:
                return self._pins[name]
            import time; time.sleep(0.05)
        return None

    def _send(self, msg):
        with self._lock:
            self._sock.sendall((json.dumps(msg) + '\n').encode())

    def _listen(self):
        while True:
            try:
                data = self._sock.recv(4096)
                if not data:
                    break
                for line in data.decode().splitlines():
                    if not line.strip():
                        continue
                    msg = json.loads(line)
                    if msg.get("action") == "pin_update":
                        self._pins[msg["name"]] = msg["value"]
            except Exception:
                break
