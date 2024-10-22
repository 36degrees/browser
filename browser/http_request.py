from browser.request import Request

import socket
import ssl

class HttpRequest(Request):
    def open(self):
        # Connect to socket
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP
        )

        s.connect((self.url.host, self.url.port))

        if self.url.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.url.host)

        headers = {
            'Host'       : self.url.host,
            'User-Agent' : 'MyTestBrowser',
            'Connection' : 'close'
        }

        # Build and send the request
        request = "GET {} HTTP/1.1\r\n".format(self.url.path)

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
