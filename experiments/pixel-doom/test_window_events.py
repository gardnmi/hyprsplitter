"""The event reader must keep draining while the main thread is busy elsewhere."""
import socket,tempfile,threading,time
from pathlib import Path
from window_events import WindowEvents
with tempfile.TemporaryDirectory(prefix='pd-events-') as d:
 path=Path(d)/'events';server=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);server.bind(str(path));server.listen(1)
 reader=WindowEvents(path,'pixel-doom-test');conn,_=server.accept();conn.settimeout(2)
 sent=threading.Event();errors=[]
 def flood():
  try:
   # Far beyond a socket buffer; sender must finish before discover is called.
   conn.sendall(b'windowtitle>>unused,'+b'x'*128+b'\n')
   for _ in range(1024):conn.sendall((b'windowtitle>>unused,'+b'x'*128+b'\n')*64)
   conn.sendall(b'openwindow>>abc,1,pixel-doom-test,pixel-doom-test-')
   conn.sendall(b'7\nopenwindow>>def,1,pixel-doom-test,pixel-doom-test--1\n')
   sent.set()
  except Exception as e:errors.append(e)
 worker=threading.Thread(target=flood);worker.start()
 assert sent.wait(3),(errors,'reader did not drain without discover')
 assert reader.discover([7,-1])=={7:'0xabc',-1:'0xdef'}
 conn.close();worker.join()
 try:reader.discover([8],timeout=2)
 except RuntimeError as e:assert 'connection closed' in str(e)
 else:raise AssertionError('disconnect was not reported')
 reader.close();assert not reader.thread.is_alive();server.close()
 print('PASS: >9 MiB event flood drained independently, fragmented open events, and disconnect cleanup')
