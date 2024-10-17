import base64
import socket
import ssl

class URL:
    is_view_source = False

    def __init__(self, url):

        if url.startswith('view-source:'):
            self.is_view_source = True
            url = url.removeprefix('view-source:')

        if url.startswith('data:'):
            self.scheme, url = url.split(":", 1)
            self.mimetype, self.body = url.split(",", 1)
            return

        self.scheme, url = url.split("://", 1)

        self.host, url = url.split("/", 1)
        self.path = "/" + url

        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)
        elif self.scheme == "https":
            self.port = 443
        else:
            self.port = 80

    def request(self):
        match self.scheme:
            case 'http' | 'https':
                return self.http_request()
            case 'file':
                return self.file_request()
            case 'data':
                return self.data_request()
            case _:
                raise ValueError("Unsupported scheme")

    def http_request(self):
        # Connect to socket
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP
        )

        s.connect((self.host, self.port))

        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        headers = {
            'Host'       : self.host,
            'User-Agent' : 'MyTestBrowser',
            'Connection' : 'close'
        }

        # Build and send the request
        request = "GET {} HTTP/1.1\r\n".format(self.path)

        for key, value in headers.items():
            request += f'{key}: {value}\r\n'

        request += "\r\n"

        s.send(request.encode("utf8"))

        # Handle the response
        response = s.makefile("r", encoding="utf8", newline="\r\n")

        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)

        # Process response headers
        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n": break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()

        # Detect things we can't handle
        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers

        # Grab response body and clean up
        content = response.read()
        s.close()

        return content
    
    def file_request(self):
        with open(self.path) as f:
            return f.read()
        
    def data_request(self):
        if self.mimetype.endswith(";base64"):
            return base64.b64decode(self.body).decode('utf-8')
        else:
            return self.body

def show(body):
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            print(c, end="")

def load(url):
    body = url.request()
    if url.is_view_source:
        print(body)
    else:
        show(body)

if __name__ == "__main__":
    import sys
    load(URL(sys.argv[1]))
