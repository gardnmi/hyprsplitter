"""A slow private response must complete once, without replaying its command."""
import socket
import tempfile
import threading
import time
import unittest
from pathlib import Path
from progressive import StressHyprland


class StressIPCTest(unittest.TestCase):
    def test_response_slower_than_original_two_second_limit(self):
        with tempfile.TemporaryDirectory(prefix='pd-ipc-test-') as directory:
            path = str(Path(directory) / 'socket')
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
                server.bind(path)
                server.listen(1)
                commands = []
                def respond():
                    conn, _ = server.accept()
                    with conn:
                        commands.append(conn.recv(4096))
                        time.sleep(2.2)
                        conn.sendall(b'ok')
                worker = threading.Thread(target=respond)
                worker.start()
                # Exercise transport against a fake server; real construction
                # separately requires the disposable compositor executable.
                client = object.__new__(StressHyprland)
                client.path = path
                self.assertEqual(client.request('eval test'), 'ok')
                worker.join(timeout=5)
                self.assertFalse(worker.is_alive())
                self.assertEqual(commands, [b'/eval test'])


if __name__ == '__main__':
    unittest.main()
