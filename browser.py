import tkinter
import tkinter.font

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
        self.pageheight = 0

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
        for x, y, c, font in self.display_list:
            # Skip off-canvas characters
            if y > self.scroll + self.height: continue
            if y + VSTEP < self.scroll: continue
            self.canvas.create_text(x, y - self.scroll, text=c, font=font, anchor='nw')

        self.render_scrollbar()

    def render_scrollbar(self):
        if self.pageheight < self.height:
            return

        size = round((self.height / self.pageheight) * self.height)
        position = round((self.scroll / self.pageheight) * self.height)

        self.canvas.create_rectangle(
            self.width - 15,
            position,
            self.width,
            position + size,
            fill="blue"
        )

    def layout(self, tokens):
        weight = "normal"
        style = "roman"

        display_list = []
        cursor_x, cursor_y = HSTEP, VSTEP
        for tok in tokens:
                if isinstance(tok, Text):
                    for word in tok.text.split():
                        font = tkinter.font.Font(
                            size=16,
                            weight=weight,
                            slant=style,
                        )
                        display_list.append((cursor_x, cursor_y, word, font))
                        w = font.measure(word)

                        if cursor_x + w > self.width - HSTEP:
                            cursor_y += font.metrics("linespace") * 1.25
                            cursor_x = HSTEP
                        else:
                            cursor_x += w + font.measure(" ")

                    self.pageheight = cursor_y
                elif tok.tag == "i":
                    style = "italic"
                elif tok.tag == "/i":
                    style = "roman"
                elif tok.tag == "b":
                    weight = "bold"
                elif tok.tag == "/b":
                    weight = "normal"
        return display_list

    def configure(self, e):
        self.height = e.height
        self.width = e.width
        print(f"resizing to {self.width} * {self.height}")
        tokens = lex(self.response.content)
        self.display_list = self.layout(tokens)
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
                self.pageheight - self.height + HSTEP
            )
        )
        self.draw()

class Text:
    def __init__(self, text):
        self.text = text

class Tag:
    def __init__(self, tag):
        self.tag = tag

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
