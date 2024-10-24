from urllib.parse import urljoin

from browser.request import Request
from browser.url import URL

def show(body):
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            print(c, end="")

def load(url_as_string):
    url = URL(url_as_string)
    response = Request.factory(url)

    redirect_count = 0
    while 300 <= int(response.status) <= 399 and 'location' in response.headers:
        if redirect_count > 10:
            raise RuntimeError('Excessive redirects')
        
        destination = urljoin(url_as_string, response.headers['location'])
        print(f'Redirecting to {destination}')

        response = Request.factory(URL(destination))
        redirect_count += 1

    if url.is_view_source:
        print(response.content)
    else:
        show(response.content)

if __name__ == "__main__":
    import sys
    load(sys.argv[1])
