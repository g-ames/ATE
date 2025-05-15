import tgfx
import os

files = os.listdir(os.getcwd())
running = False

def take(canvas):
    global files, running
    
    running = True
    files = os.listdir(os.getcwd())
    cwd = os.getcwd()
    selected = 0
    
    while running:
        pressed_key = tui.getkey()

        if pressed_key == "UpArrow":
            selected -= 1
        elif pressed_key == "DownArrow":
            selected += 1
        elif pressed_key == "\r":
            break
        
        selected = min(max(selected, 0), len(files) - 1)

        canvas.clear()
        canvas.put((0, 0), cwd)
        for fi, file in enumerate(files):
            selection_color = ((0, 0, 255) if fi != selected else (255, 0, 0))
            canvas.put((5, fi + 1), f"{str(file)}{" " * (max([len(x) for x in files])+1 - len(str(file)))}{"(directory)" if os.path.isdir(file) else '(file)'}", color=selection_color)
        canvas.print()
    
    return files[selected]