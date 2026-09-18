"""Foot 1.28 client protocol; avoid spawning footclient for every window.

Layout verified against foot's client-protocol.h and the installed CLI's output.
Callers use the ordinary CLI on other versions.
"""
import os
import socket
import struct


def packet(app, title, width, height, command, hold, cwd=None):
    cwd=os.fsencode(cwd or os.getcwd())+b'\0'
    overrides=[f'app-id={app}',f'title={title}',f'initial-window-size-pixels={width}x{height}']
    values=[*overrides,*map(str,command)]
    body=struct.pack('=BBHHHH',2|int(hold),0,len(cwd),len(overrides),len(command),0)+cwd
    for value in values:
        raw=os.fsencode(value)+b'\0'
        if len(raw)>65535: raise ValueError('Foot protocol string too long')
        body+=struct.pack('=H',len(raw))+raw
    return struct.pack('=I',len(body))+body


def open_window(server, app, title, width, height, command, hold):
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as connection:
        connection.settimeout(15)
        connection.connect(str(server))
        connection.sendall(packet(app,title,width,height,command,hold))
        answer=b''
        while len(answer)<4:
            chunk=connection.recv(4-len(answer))
            if not chunk: raise RuntimeError('Foot closed the creation request')
            answer+=chunk
        status=struct.unpack('=i',answer)[0]
        if status: raise RuntimeError(f'Foot failed to open {title}: {status}')
