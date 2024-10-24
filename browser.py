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

def load(url):
    response = Request.factory(url)

    redirect_count = 0
    while 300 <= int(response.status) <= 399 and 'location' in response.headers:
        if redirect_count > 10:
            raise RuntimeError('Excessive redirects')
        print(f'Redirecting to {response.headers['location']}')
        response = Request.factory(URL(response.headers['location']))
        redirect_count += 1

    if url.is_view_source:
        print(response.content)
    else:
        show(response.content)

if __name__ == "__main__":
    import sys
    load(URL(sys.argv[1]))
