import tkinter

from urllib.parse import urljoin

from browser.layout import Layout, HSTEP, VSTEP
from browser.request import Request
from browser.tag import Tag
from browser.text import Text
from browser.url import URL

INITIAL_WIDTH, INITIAL_HEIGHT = 800, 600
SCROLL_STEP = 100
class Browser:
    
    def __init__(self):
        self.window = tkinter.Tk()

        self.width = INITIAL_WIDTH
        self.height = INITIAL_HEIGHT

        self.canvas = tkinter.Canvas(
            self.window, 
            width=self.width,
            height=self.height
        )
        self.canvas.pack(fill="both", expand=1)
        self.scroll = 0

        # Window resizing
        self.window.bind("<Configure>", self.configure)

        # Key bindings
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<MouseWheel>", self.scrollwheel)

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
            tokens = lex(response.content)
            self.layout = Layout(tokens, self.width)
            self.draw()

        self.response = response

    def draw(self):
        self.canvas.delete("all")
        for x, y, c, font in self.layout.display_list:
            # Skip off-canvas characters
            if y > self.scroll + self.height: continue
            if y + VSTEP < self.scroll: continue
            self.canvas.create_text(x, y - self.scroll, text=c, font=font, anchor='nw')

        self.render_scrollbar()

    def render_scrollbar(self):
        if self.layout.pageheight < self.height:
            return

        size = round((self.height / self.layout.pageheight) * self.height)
        position = round((self.scroll / self.layout.pageheight) * self.height)

        self.canvas.create_rectangle(
            self.width - 15,
            position,
            self.width,
            position + size,
            fill="blue"
        )

    def configure(self, e):
        self.height = e.height
        self.width = e.width
        print(f"resizing to {self.width} * {self.height}")
        tokens = lex(self.response.content)
        self.layout = Layout(tokens, self.width)
        self.draw()

    def scrollup(self, e):
        self.scroll_by_delta(-1)

    def scrolldown(self, e):
        self.scroll_by_delta(1)

    def scrollwheel(self, e):
        self.scroll_by_delta(e.delta * -1)

    def scroll_by_delta(self, delta):
        # Clamp scrolling to the beginning and end of the document
        self.scroll = max(
            0,
            min(
                self.scroll + (delta * 100),
                self.layout.pageheight - self.height + HSTEP
            )
        )
        self.draw()

def lex(body):
    out = []
    buffer = ""
    in_tag = False

    for c in body:
        if c == "<":
            in_tag = True
            if buffer: out.append(Text(buffer))
            buffer = ""
        elif c == ">":
            in_tag = False
            out.append(Tag(buffer))
            buffer = ""
        else:
            buffer += c

    if not in_tag and buffer:
        out.append(Text(buffer))

    return out

if __name__ == "__main__":
    import sys
    Browser().load(sys.argv[1])
    tkinter.mainloop()
