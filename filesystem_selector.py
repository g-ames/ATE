import tgfx as tui
import os
import math
import converter
import audio_player

files = os.listdir(os.getcwd())
running = False

def take(canvas):
    global files, running
    
    running = True
    files = os.listdir(os.getcwd())
    files.append("..")
    files.sort()
    files.insert(0, "Return to origin")
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
            if fi > canvas.size[1] - 2:
                break
            selection_color = ((100, 100, 255) if fi != selected else (255, 100, 100))
            canvas.put((5, fi + 1 - selected + math.floor(canvas.size[1] / 2)), f"{str(file)}{" " * (max([len(x) for x in files])+1 - len(str(file)))}{"(directory)" if os.path.isdir(file) else '(file)'}", color=selection_color)
        canvas.print()
    
    if files[selected] == "Return to origin":
        return None # stay in the same file
    
    if os.path.isdir(files[selected]):
        os.chdir(files[selected])
        return take(canvas)

    # check if it is a binary file (like .png, .jpg, .exe, etc)
    if not os.path.isfile(files[selected]) or any([files[selected].endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".exe", ".bin", ".dll", ".so", ".dylib", ".class", ".jar", ".pyc", ".pyo", ".pyd", ".lib", ".a", ".o", ".obj", ".elf", ".sys", ".img", ".iso", ".zip", ".tar", ".gz", ".7z", ".rar", ".mp3", ".wav", ".ogg", ".flac", ".mp4", ".mkv", ".avi", ".mov", ".wmv"]]):        
        # if it is an image file, convert it to text and display it
        if any([files[selected].endswith(ext) for ext in [".png", ".jpg", ".jpeg"]]):
            converter.view_image(files[selected])
        elif any([files[selected].endswith(ext) for ext in [
            ".mp3", ".wav", ".ogg", ".flac", ".mp4", ".mkv", ".avi", ".mov", ".wmv"
        ]]):
            audio_player.play(files[selected], canvas)
        else:
            canvas.input(f"'{files[selected]}' is not a text file. Press Enter to return...")
        return take(canvas)

    return files[selected]