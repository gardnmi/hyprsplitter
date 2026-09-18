"""Checks the real CLI wire format and PTY ownership after helper exit."""
import os
from pathlib import Path
import pty
import select
import socket
import struct
import subprocess
import tempfile
import time
import unittest
from foot_ipc import packet


class TransportTests(unittest.TestCase):
    def test_matches_installed_footclient(self):
        with tempfile.TemporaryDirectory() as d:
            server=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
            server.bind(d+'/server'); server.listen(); server.settimeout(3)
            env={k:v for k,v in os.environ.items() if k not in ('XDG_ACTIVATION_TOKEN','DESKTOP_STARTUP_ID')}
            proc=subprocess.Popen(['footclient','-s',d+'/server','-N','-H','-D',d,
                                   '-a','test-app','-T','test-title','-w','20x15','/usr/bin/true'],env=env)
            try:
                connection,_=server.accept(); connection.settimeout(3)
                def read(n):
                    out=b''
                    while len(out)<n:
                        chunk=connection.recv(n-len(out))
                        if not chunk: raise RuntimeError('Unexpected EOF')
                        out+=chunk
                    return out
                header=read(4); body=read(struct.unpack('=I',header)[0])
                connection.sendall(struct.pack('=i',0)); connection.close()
                self.assertEqual(proc.wait(timeout=3),0)
                self.assertEqual(header+body,packet('test-app','test-title',20,15,['/usr/bin/true'],True,d))
            finally:
                if proc.poll() is None: proc.kill(); proc.wait()
                server.close()

    def test_pty_survives_helper_exit_and_forwards_keys(self):
        with tempfile.TemporaryDirectory() as d:
            frame=Path(d)/'frame'; frame.write_bytes(bytes([255,0,0]))
            keys=socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM)
            keys.bind(d+'/keys'); keys.settimeout(3)
            hub=subprocess.Popen(['/tmp/pixel-doom-hub',str(frame),d+'/hub',d+'/keys','2','15'])
            master,slave=pty.openpty()
            try:
                deadline=time.monotonic()+3
                while not Path(d+'/hub').exists():
                    if time.monotonic()>deadline: self.fail('Hub startup timeout')
                    time.sleep(.01)
                helper=subprocess.Popen(['/tmp/pixel-doom-hub','attach',d+'/hub','0'],
                                        stdin=slave,stdout=slave,stderr=slave)
                self.assertEqual(helper.wait(timeout=3),0)
                os.close(slave); slave=-1
                def expect(needle):
                    out=b''; deadline=time.monotonic()+3
                    while needle not in out and time.monotonic()<deadline:
                        if select.select([master],[],[],.2)[0]: out+=os.read(master,1024)
                    self.assertIn(needle,out)
                expect(b'#ff0000')
                frame.write_bytes(bytes([0,255,0])); expect(b'#00ff00')
                os.write(master,b'f'); self.assertEqual(keys.recv(128),b'f')
                os.write(master,b'q'); self.assertEqual(keys.recv(128),b'q')
                os.close(master); master=-1
                time.sleep(.1); self.assertIsNone(hub.poll())
            finally:
                hub.terminate(); hub.wait(timeout=3); keys.close()
                if master>=0: os.close(master)
                if slave>=0: os.close(slave)

    def test_progressive_regions_average_and_change_without_restarting(self):
        with tempfile.TemporaryDirectory() as d:
            frame=Path(d)/'frame'
            frame.write_bytes((bytes([255,0,0])*160+bytes([0,0,255])*160)*200)
            regions=Path(d)/'regions';regions.write_bytes(struct.pack('<I4HI',2,0,0,320,200,0))
            keys=socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM);keys.bind(d+'/keys')
            hub=subprocess.Popen(['/tmp/pixel-doom-hub',str(frame),d+'/hub',d+'/keys','1','35',str(regions)])
            master,slave=pty.openpty()
            try:
                deadline=time.monotonic()+3
                while not Path(d+'/hub').exists():
                    if time.monotonic()>deadline:self.fail('Hub startup timeout')
                    time.sleep(.01)
                helper=subprocess.Popen(['/tmp/pixel-doom-hub','attach',d+'/hub','0'],stdin=slave,stdout=slave,stderr=slave)
                self.assertEqual(helper.wait(timeout=3),0)
                def expect(needle):
                    data=b'';deadline=time.monotonic()+3
                    while needle not in data and time.monotonic()<deadline:
                        if select.select([master],[],[],.1)[0]:data+=os.read(master,1024)
                    self.assertIn(needle,data)
                expect(b'#7f007f')
                fd=os.open(regions,os.O_RDWR)
                try:
                    os.pwrite(fd,struct.pack('<I',3),0)
                    os.pwrite(fd,struct.pack('<4H',0,0,160,200),4)
                    os.pwrite(fd,struct.pack('<I',4),0)
                    expect(b'#ff0000')
                    os.pwrite(fd,struct.pack('<I',5),0)
                    os.pwrite(fd,struct.pack('<4H',160,0,320,200),4)
                    os.pwrite(fd,struct.pack('<I',6),0)
                    expect(b'#0000ff')
                    self.assertIsNone(hub.poll())
                finally:os.close(fd)
            finally:
                hub.terminate();hub.wait(timeout=3)
                keys.close();os.close(master);os.close(slave)


if __name__=='__main__': unittest.main()
