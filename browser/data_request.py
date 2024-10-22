import base64

from browser.request import Request

class DataRequest(Request):
    def open(self):
        if self.url.mimetype.endswith(";base64"):
            return base64.b64decode(self.url.body).decode('utf-8')
        else:
            return self.body
