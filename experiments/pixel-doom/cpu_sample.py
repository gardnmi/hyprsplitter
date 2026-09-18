"""Small Linux x86-64 perf sampler; user-space IPs for one explicitly supplied PID."""
import ctypes
import mmap
import os
import struct
import time
from pathlib import Path


class Sampler:
    def __init__(self, pid):
        if os.uname().machine != 'x86_64':
            raise RuntimeError('perf syscall number is specific to x86-64')
        attr=bytearray(128)
        # Software CPU clock, 100 Hz; IP+timestamp; exclude kernel/hypervisor.
        struct.pack_into('IIQQQQQ',attr,0,1,128,0,10000000,5,0,(1<<5)|(1<<6))
        struct.pack_into('I',attr,48,1)
        libc=ctypes.CDLL(None,use_errno=True)
        buffer=ctypes.create_string_buffer(bytes(attr))
        self.fd=libc.syscall(298,buffer,pid,-1,-1,0)
        if self.fd<0:
            raise OSError(ctypes.get_errno(),os.strerror(ctypes.get_errno()))
        self.pid=pid
        self.ring=mmap.mmap(self.fd,65*mmap.PAGESIZE,mmap.MAP_SHARED,mmap.PROT_READ|mmap.PROT_WRITE)
        self.maps=Path(f'/proc/{pid}/maps').read_text()
        self.started=time.monotonic()

    def finish(self):
        import fcntl
        fcntl.ioctl(self.fd,0x2401,0) # PERF_EVENT_IOC_DISABLE
        head=struct.unpack_from('Q',self.ring,1024)[0]
        tail=struct.unpack_from('Q',self.ring,1032)[0]
        offset,size=struct.unpack_from('QQ',self.ring,1040)
        data=self.ring[offset:offset+size]
        samples=[];lost=0
        while tail<head:
            pos=tail%size
            header=(data+data)[pos:pos+8]
            kind,_,length=struct.unpack('IHH',header)
            if length<8 or length>size:
                raise RuntimeError('Invalid perf ring record')
            record=(data+data)[pos:pos+length]
            if kind==9:
                ip,stamp=struct.unpack_from('QQ',record,8)
                samples.append({'ip':ip,'time_ns':stamp})
            elif kind==2:
                lost+=struct.unpack_from('Q',record,16)[0]
            tail+=length
        struct.pack_into('Q',self.ring,1032,tail)
        self.ring.close();os.close(self.fd)
        return dict(pid=self.pid,started_monotonic=self.started,ended_monotonic=time.monotonic(),
                    lost=lost,maps=self.maps,samples=samples,scope='compositor-main-thread-user-space')
