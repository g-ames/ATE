import tgfx as tui
import os
import math
import converter
import audio_player
import difflib
import shutil

def order_by_similarity(target, string_list):
    return sorted(string_list, key=lambda s: difflib.SequenceMatcher(None, target.lower(), s.lower()).ratio(), reverse=True)


files = os.listdir(os.getcwd())
running = False

def take(canvas):
    global files, running
    
    running = True
    files = os.listdir(os.getcwd())
    files.append("..")
    files.sort()
    files.insert(0, "`NEW`")
    files.insert(0, "`RETURN`")
    cwd = os.getcwd()
    selected = 0
    looking_buffer = ""

    while running:
        pressed_key = tui.getkey()

        if pressed_key == "UpArrow":
            selected -= 1
        elif pressed_key == "DownArrow":
            selected += 1
        elif pressed_key == "\r":
            break
        elif pressed_key == "Escape":
            return None
        elif pressed_key == "\b":
            looking_buffer = looking_buffer[:-1]
        elif pressed_key == "PageDown" or pressed_key == "PageUp":
            selected += (canvas.size[1] * (1 if pressed_key == "PageDown" else -1))
            if selected >= len(files):
                selected = len(files) - 1
        elif pressed_key != None:
            looking_buffer += pressed_key
            looking_buffer = looking_buffer.strip()
            if looking_buffer != "":
                files = order_by_similarity(looking_buffer, files)
                selected = 0
        selected = min(max(selected, 0), len(files) - 1)

        canvas.clear()
        canvas.put((0, 0), cwd)

        for fi, file in enumerate(files):
            if fi > canvas.size[1] - 2:
                break
            selection_color = ((100, 100, 255) if fi != selected else (255, 100, 100))
            canvas.put((5, fi + 1 - selected + math.floor(canvas.size[1] / 2)), f"{str(file)}{" " * (max([len(x) for x in files])+1 - len(str(file)))}{"(directory)" if os.path.isdir(file) else '(file)'}", color=selection_color)
        
        canvas.put((3, tui.get_terminal_size()[1] - 3), looking_buffer, color=(255, 255, 255))
        canvas.print()
    
    # new file
    if files[selected] == "`NEW`":
        filename = canvas.input("Name: ")
        open(filename, "a").close()
        return filename
    
    if files[selected] == "`RETURN`":
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
        elif not shutil.which(files[selected]) is None:
            os.startfile(files[selected])
        else:
            canvas.input(f"'{files[selected]}' is not a text file. Press Enter to return...")
        return take(canvas)

    return files[selected]