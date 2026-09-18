"""Continuously drain compositor events while the main thread places windows."""
import socket
import threading
import time


class WindowEvents:
    def __init__(self, path, app):
        self.app = app
        self.windows = {}
        self.error = None
        self.condition = threading.Condition()
        self.stopping = threading.Event()
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(.25)
        self.sock.connect(str(path))
        self.thread = threading.Thread(target=self._read, name='pixel-doom-events', daemon=True)
        self.thread.start()

    def _read(self):
        pending = b''
        try:
            while not self.stopping.is_set():
                try:
                    data = self.sock.recv(65536)
                except socket.timeout:
                    continue
                if not data:
                    raise RuntimeError('Compositor event connection closed')
                pending += data
                lines = pending.split(b'\n')
                pending = lines.pop()
                for line in lines:
                    if not line.startswith(b'openwindow>>'):
                        continue
                    fields = line.decode(errors='replace').split('>>', 1)[1].split(',', 3)
                    if len(fields) != 4 or fields[2] != self.app:
                        continue
                    prefix = self.app + '-'
                    if not fields[3].startswith(prefix):
                        continue
                    try:
                        index = int(fields[3][len(prefix):])
                    except ValueError:
                        continue
                    with self.condition:
                        self.windows[index] = '0x' + fields[0].removeprefix('0x')
                        self.condition.notify_all()
        except (OSError, RuntimeError) as error:
            if not self.stopping.is_set():
                with self.condition:
                    self.error = error
                    self.condition.notify_all()

    def discover(self, indices, timeout=20):
        indices = list(indices)
        deadline = time.monotonic() + timeout
        with self.condition:
            while True:
                if self.error:
                    raise RuntimeError(str(self.error)) from self.error
                if all(i in self.windows for i in indices):
                    return {i: self.windows[i] for i in indices}
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError('Window-open events timed out')
                self.condition.wait(remaining)

    def close(self):
        self.stopping.set()
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.thread.join(timeout=2)
        self.sock.close()
