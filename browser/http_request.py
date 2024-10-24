import gzip

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
            'Accept-Encoding': 'gzip'
        }

        # Build and send the request
        request = "GET {} HTTP/1.1\r\n".format(self.url.path)

        for key, value in headers.items():
            request += f'{key}: {value}\r\n'

        request += "\r\n"

        s.send(request.encode("utf8"))

        # Handle the response
        response = s.makefile("rb", encoding="utf8", newline="\r\n")

        statusline = response.readline().decode(encoding='utf-8')
        print(f'Statusline: {statusline}')
        version, self.status, explanation = statusline.split(" ", 2)

        # Process response headers
        response_headers = {}
        while True:
            line = response.readline().decode(encoding='utf-8')
            if line == "\r\n": break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()

        self.headers = response_headers

        # Grab response body and clean up
        if 'content-length' in response_headers:
            content_length = int(response_headers["content-length"])
        else:
            content_length = -1

        if response_headers.get('transfer-encoding') == 'chunked':
            content = b''
            while True:
                chunk_length = response.readline().strip().decode(encoding='utf-8')
                if chunk_length == '0' or not chunk_length:
                    response.readline()
                    break

                content += response.read(int(chunk_length, 16))

                # Consume trailing new line
                response.read(2)
        else:
            content = response.read(content_length)

        if response_headers.get('content-encoding') == 'gzip':
            content = gzip.decompress(content)

        self.content = content.decode(encoding='utf-8')
