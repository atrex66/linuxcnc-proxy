#!/usr/bin/env python3
"""
linuxcnc_proxy.py
A headless TCP/IP proxy for LinuxCNC with status, command, and error channels.
"""
import socket
import threading
import time


STATUS_PORT = 5000
COMMAND_PORT = 5001
ERROR_PORT = 5002
HAL_PORT = 5003
DISCOVERY_PORT = 5009
DISCOVERY_MAGIC = b'LINUXCNC_DISCOVER'
DISCOVERY_REPLY_MAGIC = b'LINUXCNC_HERE'
HOST = '0.0.0.0'

import threading
try:
    import hal
except ImportError:
    hal = None

# In-memory pin registry for demo/prototype
hal_pins = {}

def handle_hal(conn, addr):
    print(f"[HAL] Remote host connected: {addr}")
    global hal_pins
    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break
            msg = json.loads(data.decode().strip())
            action = msg.get("action")
            if action == "create_pin":
                name = msg["name"]
                ptype = msg["type"]
                direction = msg["dir"]
                # Create pin in real HAL if available
                if hal:
                    if direction == "in":
                        hal.newpin(name, hal.HAL_BIT if ptype=="bit" else hal.HAL_FLOAT, hal.HAL_IN)
                    else:
                        hal.newpin(name, hal.HAL_BIT if ptype=="bit" else hal.HAL_FLOAT, hal.HAL_OUT)
                hal_pins[name] = {"type": ptype, "dir": direction, "value": False if ptype=="bit" else 0.0}
                conn.sendall((json.dumps({"action": "create_pin", "result": "ok", "name": name}) + '\n').encode())
            elif action == "set_pin":
                name = msg["name"]
                value = msg["value"]
                if name in hal_pins:
                    hal_pins[name]["value"] = value
                    # Set value in real HAL if available
                    if hal:
                        hal_pins[name]["halpin"].set(value)
                    conn.sendall((json.dumps({"action": "set_pin", "result": "ok", "name": name}) + '\n').encode())
            elif action == "get_pin":
                name = msg["name"]
                value = hal_pins.get(name, {}).get("value")
                conn.sendall((json.dumps({"action": "pin_update", "name": name, "value": value}) + '\n').encode())
            elif action == "ready":
                conn.sendall((json.dumps({"action": "ready", "result": "ok"}) + '\n').encode())
        except Exception as e:
            print(f"[HAL] Error: {e}")
            break
    conn.close()
def discovery_responder():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.bind((HOST, DISCOVERY_PORT))
    while True:
        try:
            data, addr = s.recvfrom(1024)
            if data.startswith(DISCOVERY_MAGIC):
                s.sendto(DISCOVERY_REPLY_MAGIC, addr)
        except Exception:
            continue



# Try to import real linuxcnc, otherwise fallback to stub
try:
    import linuxcnc
    class LinuxCNCReal:
        def __init__(self):
            self.stat = linuxcnc.stat()
            self.command = linuxcnc.command()
            self.error = linuxcnc.error()

        def poll_status(self):
            self.stat.poll()
            # Example: return state and position
            return {
                "state": self.stat.state,
                "position": list(self.stat.position) if hasattr(self.stat, 'position') else None
            }

        def execute_command(self, cmd):
            # cmd is a dict: {"cmd": ..., "args": ..., "kwargs": ...}
            try:
                method = getattr(self.command, cmd["cmd"])
                result = method(*cmd.get("args", []), **cmd.get("kwargs", {}))
                return {"result": result}
            except Exception as e:
                return {"error": str(e)}

        def poll_error(self):
            # If linuxcnc has error reporting, implement here
            return self.error

    linuxcnc = LinuxCNCReal()
except ImportError:
    import ast
    import json
    class LinuxCNCStub:
        def __init__(self):
            self.status = {"state": "idle", "position": [0, 0, 0]}
            self.error = None

        def poll_status(self):
            return self.status

        def execute_command(self, cmd):
            print(f"[STUB] Executing command: {cmd}")
            return {"result": "ok"}

        def poll_error(self):
            return self.error

    linuxcnc = LinuxCNCStub()


import json
def handle_status(conn, addr):
    print(f"[STATUS] Remote host connected: {addr}")
    while True:
        try:
            status = linuxcnc.poll_status()
            conn.sendall((json.dumps(status) + '\n').encode())
            time.sleep(1)
        except Exception:
            break
    conn.close()

def handle_command(conn, addr):
    print(f"[COMMAND] Remote host connected: {addr}")
    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break
            try:
                cmd = json.loads(data.decode().strip())
            except Exception:
                # fallback for eval-based clients
                cmd = ast.literal_eval(data.decode().strip())
            print(f"Received command: {cmd}")
            result = linuxcnc.execute_command(cmd)
            conn.sendall((json.dumps(result) + '\n').encode())
        except Exception:
            break
    conn.close()

def handle_error(conn, addr):
    print(f"[ERROR] Remote host connected: {addr}")
    while True:
        try:
            error = linuxcnc.poll_error()
            conn.sendall((json.dumps({"error": error}) + '\n').encode())
            time.sleep(2)
        except Exception:
            break
    conn.close()

def start_server(port, handler):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, port))
    s.listen()
    print(f"Listening on {HOST}:{port}")
    while True:
        conn, addr = s.accept()
        print(f"Connection from {addr} on port {port}")
        threading.Thread(target=handler, args=(conn, addr), daemon=True).start()

def main():
    threading.Thread(target=discovery_responder, daemon=True).start()
    threading.Thread(target=start_server, args=(STATUS_PORT, handle_status), daemon=True).start()
    threading.Thread(target=start_server, args=(COMMAND_PORT, handle_command), daemon=True).start()
    threading.Thread(target=start_server, args=(ERROR_PORT, handle_error), daemon=True).start()
    threading.Thread(target=start_server, args=(HAL_PORT, handle_hal), daemon=True).start()
    print("LinuxCNC Proxy running (headless)...")
    while True:
        time.sleep(10)

if __name__ == "__main__":
    main()
