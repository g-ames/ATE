import subprocess
import threading
import time
import os
import tgfx

import re
ansi_escape = re.compile(r'\x1b[^m]*m')

def clean_text(text):
    return ansi_escape.sub('', text)

# Single canvas for all panes
canvas = tgfx.Canvas()
canvas_size = canvas.size

# Set the background so old characters are cleared
canvas.background = " "  # you can also use "." if you prefer

# Pane class wraps a shell subprocess


class Pane:
    def __init__(self, pos, size, shell_cmd):
        self.pos = pos          # (x, y) top-left corner
        self.size = size        # (width, height)
        self.proc = subprocess.Popen(
            shell_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=0
        )
        self.buffer = []
        self.lock = threading.Lock()
        self.output_thread = threading.Thread(
            target=self.read_output, daemon=True)
        self.output_thread.start()

    def read_output(self):
        while True:
            char = self.proc.stdout.read(1)
            if not char:
                break
            try:
                text = char.decode(errors='ignore')
            except:
                continue
            with self.lock:
                self.buffer.append(text)
            self.render_buffer()


    def render_buffer(self):
        with self.lock:
            lines = "".join(self.buffer).split("\n")
            for y, line in enumerate(lines[-self.size[1]:]):
                # fill line with background first
                clear_line = canvas.background * self.size[0]
                canvas.put((self.pos[0], self.pos[1] + y), clean_text(clear_line))
                # then write the actual text
                canvas.put((self.pos[0], self.pos[1] + y), clean_text(line))
        canvas.print()

    def send_input(self, char):
        if self.proc.stdin:
            self.proc.stdin.write(char.encode())
            self.proc.stdin.flush()


# Setup panes
shell_cmd = ["bash"] if os.name != "nt" else ["cmd.exe"]
pane1 = Pane((0, 0), (canvas_size[0]//2, canvas_size[1]//2), shell_cmd)
pane2 = Pane((canvas_size[0]//2, 0),
             (canvas_size[0]//2, canvas_size[1]//2), shell_cmd)
pane3 = Pane((0, canvas_size[1]//2), (canvas_size[0],
             canvas_size[1]//2), shell_cmd)  # bottom full-width
panes = [pane1, pane2, pane3]
active = 0

tgfx.hide_cursor()
try:
    while True:
        key = tgfx.getkey(blocking=True)
        if key == "Tab":
            active = (active + 1) % len(panes)  # switch active pane
        elif key == "\x03":  # Ctrl+C
            break
        else:
            panes[active].send_input(key)
finally:
    tgfx.show_cursor()
