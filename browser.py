import tkinter

from urllib.parse import urljoin

from browser.request import Request
from browser.url import URL

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100
class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window, 
            width=WIDTH,
            height=HEIGHT
        )
        self.canvas.pack()
        self.scroll = 0

        self.window.bind("<Down>", self.scrolldown)

    def load(self, url_as_string):
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
            self.print(response.content)
        else:
            text = lex(response.content)
            self.display_list = layout(text)
            self.draw()

    def draw(self):
        self.canvas.delete("all")
        for x, y, c in self.display_list:
            # Skip off-canvas characters
            if y > self.scroll + HEIGHT: continue
            if y + VSTEP < self.scroll: continue
            self.canvas.create_text(x, y - self.scroll, text=c)

    def scrolldown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()

def lex(body):
    text = ""
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            text += c
    return text

def layout(text):
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP
    for c in text:
        display_list.append((cursor_x, cursor_y, c))
        cursor_x += HSTEP
        if cursor_x >= WIDTH - HSTEP:
            cursor_y += VSTEP
            cursor_x = HSTEP
    return display_list

if __name__ == "__main__":
    import sys
    Browser().load(sys.argv[1])
    tkinter.mainloop()
