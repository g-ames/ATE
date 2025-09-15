import tgfx
import os

def pretick(canvas, _):
    # canvas.background = "█"
    return

def posttick(canvas, glob):
    canvas.move((21, 0))

    canvas.rect(0, 0, 20, tgfx.get_terminal_size()[1]-1, "█")

    # print the files in the fs
    listed = os.listdir()
    listed_better = []
    for filedir in listed:
        if filedir == glob["last_saved"]:
            continue

        if len(filedir) > 20:
            listed_better.append(filedir[:(20 - 3)] + "...")
        else:
            listed_better.append(filedir)
    
    canvas.rect(0, 1, 20, len(listed_better) + 3, "█", color=(127, 127, 127))
    last_saved = "unsaved" if glob["last_saved"] == None else glob["last_saved"]
    canvas.put((0, 1), last_saved, color=((100, 100, 255) if os.path.exists(last_saved) else (255, 100, 100))) # current file
    canvas.put((0, 2), "\n".join(listed_better), color=(255, 255, 255))
    canvas.put((0, len(listed_better) + 3), f"{len(listed)} files", color=(255, 255, 255,))