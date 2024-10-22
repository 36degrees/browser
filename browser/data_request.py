import base64

from browser.request import Request

class DataRequest(Request):
    def __init__(self, url):
        super().__init__(url)
        if self.url.mimetype.endswith(";base64"):
            self.content = base64.b64decode(self.url.body).decode('utf-8')
        else:
            self.content = self.url.body
