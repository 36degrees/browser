class Request:

    def factory(url):
        match url.scheme:
            case 'http' | 'https':
                from browser.http_request import HttpRequest
                return HttpRequest(url)
            case 'file':
                from browser.file_request import FileRequest
                return FileRequest(url)
            case 'data':
                from browser.data_request import DataRequest
                return DataRequest(url)
            case _:
                raise ValueError("Unsupported scheme")
            
    def __init__(self, url):
        self.url = url
        self.headers = {}
        self.content = ""
        self.status = 0
