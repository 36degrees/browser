from browser.request import Request
from browser.socket import create_socket
class HttpRequest(Request):
    def __init__(self, url):
        super().__init__(url)

        s = create_socket(
            self.url.host,
            self.url.port,
            self.url.scheme == "https"
        )

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
        print(f'Statusline: {statusline}')
        version, self.status, explanation = statusline.split(" ", 2)

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

        self.headers = response_headers

        # Grab response body and clean up
        self.content = response.read()
