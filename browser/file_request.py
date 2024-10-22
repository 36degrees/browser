from browser.request import Request

class FileRequest(Request):
    def __init__(self, url):
        super().__init__(url)
        with open(self.url.path) as f:
            self.content = f.read()
