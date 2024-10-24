import tkinter

from urllib.parse import urljoin

from browser.request import Request
from browser.url import URL

INITIAL_WIDTH, INITIAL_HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
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
            text = lex(response.content)
            self.display_list = self.layout(text)
            self.draw()

        self.response = response

    def draw(self):
        self.canvas.delete("all")
        for x, y, c in self.display_list:
            # Skip off-canvas characters
            if y > self.scroll + self.height: continue
            if y + VSTEP < self.scroll: continue
            self.canvas.create_text(x, y - self.scroll, text=c)

    def layout(self, text):
        display_list = []
        cursor_x, cursor_y = HSTEP, VSTEP
        for c in text:
            if c == "\n":
                cursor_x = 0
                cursor_y += HSTEP * 2
                continue

            display_list.append((cursor_x, cursor_y, c))
            cursor_x += HSTEP
            if cursor_x >= self.width - HSTEP:
                cursor_y += VSTEP
                cursor_x = HSTEP
        return display_list

    def configure(self, e):
        self.height = e.height
        self.width = e.width
        print(f"resizing to {self.width} * {self.height}")
        text = lex(self.response.content)
        self.display_list = self.layout(text)
        self.draw()

    def scrollup(self, e):
        self.scroll = max(self.scroll - SCROLL_STEP, 0)
        self.draw()

    def scrolldown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()

    def scrollwheel(self, e):
        self.scroll = max(self.scroll - (e.delta * 100), 0)
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

if __name__ == "__main__":
    import sys
    Browser().load(sys.argv[1])
    tkinter.mainloop()
