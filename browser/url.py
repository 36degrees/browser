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
