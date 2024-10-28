import tkinter
import tkinter.font

from browser.tag import Tag
from browser.text import Text

HSTEP, VSTEP = 13, 18

class Layout:

    def __init__(self, tokens, width):
        self.cursor_x = HSTEP
        self.cursor_y = VSTEP
        self.weight = "normal"
        self.style = "roman"
        self.width = width

        self.pageheight = 0

        self.display_list = []

        for tok in tokens:
            self.token(tok)

    def token(self, tok):
            if isinstance(tok, Text):
                for word in tok.text.split():
                    self.word(word)
            elif tok.tag == "i":
                style = "italic"
            elif tok.tag == "/i":
                style = "roman"
            elif tok.tag == "b":
                weight = "bold"
            elif tok.tag == "/b":
                weight = "normal"

    def word(self, word):
        font = tkinter.font.Font(
            size=16,
            weight=self.weight,
            slant=self.style,
        )
        self.display_list.append((self.cursor_x, self.cursor_y, word, font))
        w = font.measure(word)

        if self.cursor_x + w > self.width - HSTEP:
            self.cursor_y += font.metrics("linespace") * 1.25
            self.cursor_x = HSTEP
        else:
            self.cursor_x += w + font.measure(" ")

        self.pageheight = self.cursor_y
