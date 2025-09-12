import math
import numpy as np
import tgfx

shifting = 0

def get_frame(w, h, shifting):
    # Coordinate grid (centered)
    x = np.linspace(-1, 1, w)
    y = np.linspace(-1, 1, h)
    xx, yy = np.meshgrid(x, y)

    # Simple rotation
    angle = shifting * 0.05
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    xr = xx * cos_a - yy * sin_a
    yr = xx * sin_a + yy * cos_a

    # Fake "depth" without sqrt
    dist = (xr * xr + yr * yr) + 0.5

    # Scale pulsation
    z = 1.0 + 0.3 * math.sin(shifting * 0.03)

    u = xr / dist * z * 40
    v = yr / dist * z * 40

    # Simple rainbow: just phase shift one wave
    base = np.sin(u * 0.1 + shifting * 0.1)
    r = ((base + 1) * 127).astype(np.uint8)
    g = ((np.sin(base + 2.0) + 1) * 127).astype(np.uint8)
    b = ((np.sin(base + 4.0) + 1) * 127).astype(np.uint8)

    return r, g, b

def pretick(canvas):
    return

def posttick(canvas):
    global shifting
    w, h = tgfx.get_terminal_size()
    r, g, b = get_frame(w, h, shifting)

    # Plot directly
    for y in range(h):
        for x in range(w):
            if canvas.is_empty((x, y)):
                canvas.plot(x, y, "█", color=(int(r[y, x]), int(g[y, x]), int(b[y, x])))

    shifting += 1
