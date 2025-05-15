import os
import sys
import random
import time
from os import system
from PIL import Image

RESET_COLOR = "\u001b[0m"
def rgb_ansi(color):
    return f"\u001b[38;2;{round(color[0])%256};{round(color[1])%256};{round(color[2])%256}m"

def get_terminal_size():
    try:
        columns, rows = os.get_terminal_size()
        return (columns, rows)
    except OSError:
        return 80, 24

def preserved_scale(width, height, maxdim=25):
    new_width, new_height = width, height
    if new_width > new_height:
        new_height *= maxdim / new_width
        new_width = maxdim
    elif new_width < new_height:
        new_width *= maxdim / new_height
        new_height = maxdim
    else:
        new_width, new_height = maxdim, maxdim
    new_width *= 2 # preserve aspect ratio!
    return [round(new_width), round(new_height)]

def string_similarity(string1, string2):
    if len(string1) > len(string2):
        string2 += " " * (len(string1) - len(string2))
    if len(string1) < len(string2):
        string1 += " " * (len(string2) - len(string1))

    diff_count = sum(1 for a, b in zip(string1, string2) if a != b)
    return 1 - (diff_count / len(string1))

internal_buffer = ""
line_buffer = {}
interlace_ticker = False
def print(then="", remove=0, end="\n", mode='individually', similarity=1, pixel_based=False, interlace=False):
    then = str(then)
    global internal_buffer, interlace_ticker, line_buffer

    if mode == "batch":
        # Clear the specified number of lines above the current one
        removal = '\033[F\033[K' * remove if remove > 0 else ''
        sys.stdout.write(f"{removal}{then}{end}")
        sys.stdout.flush()
        return
    
    internal_buffer = ""
    if mode == "individually":
        def output(text):
            sys.stdout.write(text)
    elif mode == "individually-buffered":
        def output(text):
            global internal_buffer
            internal_buffer += text

    # "individually" mode: Clear each line separately
    if remove:
        output('\033[F' * remove)

    # Print each line individually after clearing
    lines = then.split('\n')
    for i, line in enumerate(lines):
        interlace_ticker = not interlace_ticker
        if i in line_buffer:
            if line_buffer[i] == line or (similarity != None and (string_similarity(line, line_buffer[i]) > similarity)): # check how close they are!!!
                output("\033[B") # ie if the line is the same as it was the last frame, don't change it!
                continue
        if interlace and interlace_ticker:
            output("\033[B")
            continue
        line_buffer[i] = line
        output("\033[K" + line)
        if i < len(lines) - 1 or end == "\n":
            output("\n")
    if end != "\n":
        output(end)

    if mode == "individually-buffered":
        sys.stdout.write(internal_buffer)
        sys.stdout.flush()

class TextImage():
    def __init__(self, as_text, escapes):
        self.as_text = as_text
        self.escapes = escapes

class ImageConverter():
    def __init__(self):
        self.color = "rgb"
        self.character_gradient = " .\'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
        self.color_every = 0
        self.color_divisor = 1
        self.color_closeness = 0
        self.skip_every = None
        self.color_multiplier = [1, 1, 1]
        self.maximum_dimension = 25
        self.size = (25, 25) 
    def convert(self, width, height, pixels):
        gradient = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "[::-1]

        if self.character_gradient != None:
            gradient = self.character_gradient

        res = ""
        skip_ticker = 0
        color_ticker = 0
        color_insertion = None
        last_color_insertion = None
        escapes = {}

        for y in range(height):
            skip_ticker += 1
            if skip_ticker == self.skip_every:
                skip_ticker = 0
                res += "\n"
                continue
            for x in range(width):
                px = pixels[x, y]
                bw = ((px[0]+px[1]+px[2])/3)/255
                
                color_ticker += 1
                if self.color == "rgb" and color_ticker >= self.color_every:
                    color_ticker = 0
                    color_insertion = [round(px[0] / self.color_divisor) * self.color_divisor, round(px[1] / self.color_divisor) * self.color_divisor, round(px[2] / self.color_divisor) * self.color_divisor]
                    if last_color_insertion != color_insertion:
                        value = f"\u001b[38;2;{round(color_insertion[0]*self.color_multiplier[0])};{round(color_insertion[1]*self.color_multiplier[1])};{round(color_insertion[2]*self.color_multiplier[2])}m"
                        if last_color_insertion == None: # Color closeness
                            escapes[(x, y)] = value
                            # res += value
                        else:
                            difference = abs(color_insertion[0] - last_color_insertion[0]) + abs(color_insertion[1] - last_color_insertion[1]) + abs(color_insertion[2] - last_color_insertion[2])
                            if difference > self.color_closeness:
                                escapes[(x, y)] = value
                                # res += value
                    last_color_insertion = color_insertion
                
                res += gradient[round(bw * (len(gradient)-1))]
            res += "\n"
        
        if self.color != None:
            res += "\u001b[0m"

        return TextImage(res, escapes)
    def convert_image_file(self, filename, color='rgb'):
        image = Image.open(filename)

        width, height = image.size

        new_width = width
        new_height = height

        if self.size == None:
            new_width, new_height = preserved_scale(width, height, maxdim=self.maximum_dimension)
        else:
            new_width, new_height = self.size[0], self.size[1]
        
        resized_image = image.resize((new_width, new_height))

        pixels = resized_image.load()

        return self.convert(new_width, new_height, pixels)

# Windows only... sorry.
import msvcrt
def getkey():
    if msvcrt.kbhit():
        char = msvcrt.getch()
        if char == b'\x1b':
            return "Escape"
        elif char == b'\xe0':
            char_after = msvcrt.getch()
            # print(char_after) 
            match char_after:
                case b'H': 
                    return "UpArrow"
                case b'K': 
                    return "LeftArrow"
                case b'P': 
                    return "DownArrow"
                case b'M': 
                    return "RightArrow"
                case b'\x8d': return "Control+UpArrow"
                case b's': return "Control+LeftArrow"
                case b'\x91': return "Control+DownArrow"
                case b't': return "Control+RightArrow"
        else:
            return char.decode('ASCII')
    return None

def hide_cursor():
    print('\033[?25l', end="")

def show_cursor():
    print('\033[?25h', end="")

import types
import traceback

def raise_with_traceback(exc_type, exc_value, exc_traceback):
    raise exc_value.with_traceback(exc_traceback)

def handle_exception(exc_type, exc_value, exc_traceback):
    show_cursor()
    raise exc_value.with_traceback(exc_traceback)

sys.excepthook = handle_exception

class Canvas():
    def __init__(self, size=None):
        self.auto_scale = (size == None) 
        self.size = size if size != None else get_terminal_size()
        self.size = (self.size[0], self.size[1] - 1)
        self.data = {}
        self.background = "."
        self.hasprinted = False
        self.spacing = ""
        self.images = {}
        self.remove_previous_lines = True
        self.image_converter = ImageConverter()
        self.escapes = {} 
        self.print_mode = "individually"
        self.tab_replacement = "    "
    def plot(self, x, y, fill="*"):
        self.data[(round(x), round(y))] = fill
    def plot_color(self, x, y, color=None):
        self.data[(round(x), round(y))] = f"{'' if color == None else rgb_ansi(color)}{self.data[(round(x), round(y))]}{RESET_COLOR}"
    def rect(self, x, y, w, h, fill="*"):
        for xi in range(w):
            for yi in range(h):
                self.plot(xi + x, yi + y, fill=fill)
    def shade(self, x, y, w, h, cb=(lambda x, y : "*")):
        dictonary = {}
        for xi in range(w):
            for yi in range(h):
                dictonary["X"] = xi + x
                dictonary["Y"] = yi + y
                dictonary["V"] = self.data[(xi, yi)] if (xi, yi) in self.data else None
                self.plot(xi + x, yi + y, fill=cb(dictonary))
    def line(self, start, end, fill="*"): 
        x1, y1, x2, y2 = round(start[0]), round(start[1]), round(end[0]), round(end[1])
        m_new = 2 * (y2 - y1) 
        slope_error_new = m_new - (x2 - x1) 
  
        y = y1 
        for x in range(x1, x2+1): 
  
            self.plot(x, y, fill=fill) 
  
            slope_error_new = slope_error_new + m_new 
  
            if (slope_error_new >= 0): 
                y = y+1
                slope_error_new = slope_error_new - 2 * (x2 - x1) 
    def clear(self):
        self.data = {}
    def move(self, by):
        res = {}
        for key, item in self.data.items():
            key = (key[0] + by[0], key[1] + by[1])
            if key[0] >= 0 and key[1] >= 0 and key[0] < self.size[0] and key[1] < self.size[1]:
                res[key] = item
        self.data = res
    def flip(self, horizontal=False, vertical=False):
        res = {}
        for key, item in self.data.items():
            key = (key[0] if not horizontal else -key[0], key[1] if not vertical else -key[1])
            res[key] = item
        self.data = res
    def put(self, pos, text, color=None):
        for i, char in enumerate(text):
            self.plot(i + pos[0], pos[1], fill=char)
            self.plot_color(i + pos[0], pos[1], color=color)
    def image(self, pos, size, image_filename):
        self.image_converter.size = size
        text_image = self.image_converter.convert_image_file(image_filename)
        lines = text_image.as_text.split("\n")
        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                self.plot(pos[0] + x, pos[1] + y, fill=f"{text_image.escapes[(x, y)] if (x, y) in text_image.escapes else ''}{char}")
    def message(self, text, color=None):
        while getkey() == None:
            self.put((0, self.size[1] - 1), f"{text}{" " * self.size[0]}", color=color)
            self.print()
    def input(self, preface=" $ "):
        output = ""
        
        current_key = getkey()
        while not current_key == "\r":
            if current_key == "\b":
                output = output[:-1]
            else:
                output += current_key if current_key != None else ''
            
            current_key = getkey()
            self.put((0, self.size[1] - 1), " " * self.size[0])
            self.put((0, self.size[1] - 1), f"{preface}{output}")
            self.print()
        
        return output
    def print(self):
        # most certainly not the best way...
        res = ""
        for y in range(0, self.size[1]):
            for x in range(0, self.size[0]):
                res += f"{self.data[(x, y)] if (x, y) in self.data else self.background}{self.spacing}"
            res += "\n"
        
        res = res.replace("\t", self.tab_replacement)
        if self.remove_previous_lines:
            print(res, remove=(self.size[1]) if self.hasprinted else 0, end="", mode=self.print_mode)
        else:
            print(res, remove=0, end="", mode=self.print_mode)
        
        self.hasprinted = True

        if self.auto_scale:
            self.size = get_terminal_size()
            self.size = (self.size[0], self.size[1] - 1)
    def bool_query(self, text):
        valid_response = False
        response = None
        while not valid_response:
            save_response = self.input(text).strip().lower()
            if save_response == "yes" or save_response == "y":
                valid_response = True
                response = True
            elif save_response == "no" or save_response == "n":
                valid_response = True
                response = False
        return response