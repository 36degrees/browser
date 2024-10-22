from browser.request import Request

class FileRequest(Request):
    def open(self):
        with open(self.url.path) as f:
            return f.read()
