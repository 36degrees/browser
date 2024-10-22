from functools import lru_cache

import socket
import ssl

def create_socket(host, port, is_ssl):
    print(f'Creating socket for {host}:{port}')
    s = socket.socket(
        family=socket.AF_INET,
        type=socket.SOCK_STREAM,
        proto=socket.IPPROTO_TCP
    )

    s.connect((host, port))

    if is_ssl:
        ctx = ssl.create_default_context()
        s = ctx.wrap_socket(s, server_hostname=host)

    return s
