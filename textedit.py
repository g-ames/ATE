import filesystem_selector
import syntax
import os
import time
import tgfx

tui.hide_cursor()

canvas = tui.Canvas()
canvas.background = " "
lines = [""]
position = [0, 0]
running = True
cursor_blink = time.time()
last_saved = None

color_table = {
    "alnum" : (226, 212, 186),
    "digit" : (234, 249, 217),
    "other" : (141, 128, 173),
    "double_string" : (226, 109, 90),
    "single_string" : (173, 50, 31),
    "keyword" : (24*2, 54*2, 66*2),
    "comment" : (3*3, 25*3, 39*3),
    "escapes" : (173 // 2, 50 // 2, 31 // 2)
}

special_colorizations = {
    "True" : (10, 205, 255),
    "False" : (10, 205, 255),
    "true" : (10, 205, 255),
    "false" : (10, 205, 255),
    "null" : (82, 43, 41),
    "enumerate" : (173, 50, 31),
    "\"Hello, World!\"" : (226, 109, 200)
}

def apply_quickfixes():
    global position, lines
    position[1] = max(position[1], 0)
    position[0] = max(position[0], 0)
    while len(lines) <= position[1]: lines.append("")
    if position[0] > len(lines[position[1]]): position[0] = len(lines[position[1]])

def write_file(filename, backup=True):
    open(f"{filename}{".ate" if backup else ""}", "w", encoding='utf-8').write("\n".join(lines))

def find_all_indexes(text, sub):
    indexes = []
    start_index = 0
    while True:
        index = text.find(sub, start_index)
        if index == -1:
            break
        indexes.append(index)
        start_index = index + 1
    return indexes

while running:
    pressed_key = tui.getkey()
    if pressed_key != None and "Arrow" in pressed_key:
        cursor_blink = time.time()
    match pressed_key:
        case None: pass
        case "UpArrow" | "Control+UpArrow": position[1] -= 1
        case "DownArrow" | "Control+DownArrow": position[1] += 1
        case "LeftArrow" | "Control+LeftArrow": 
            position[0] -= 1
            current_line = lines[position[1]]
            if "Control+" in pressed_key:
                while current_line[position[0]] != " " and not position[0] == 0:
                    position[0] -= 1
        case "RightArrow" | "Control+RightArrow": 
            position[0] += 1
            current_line = lines[position[1]]
            if "Control+" in pressed_key:
                while (not position[0] >= len(current_line)) and current_line[position[0]] != " ":
                    position[0] += 1
        case '\r': 
            before = lines[position[1]]
            lines[position[1]] = before[0:position[0]]
            lines.insert(position[1]+1, before[position[0]:len(before)])

            position[0] = 0
            position[1] += 1
        case "Escape":
            commands = canvas.input()
            
            if commands.startswith("!"):
                print('\n'*canvas.size[1])
                os.system(f"{commands[1:]}")
                input("PRESS ENTER TO CONTINUE")
                print('\n'*canvas.size[1])
                continue
            
            commands_list = commands.lower().split(";")
            for commands in commands_list:
                commands = commands.split(" ")
                match commands[0]:
                    case "quit" | "exit" | "q" | "ex":
                        if commands[0] == "exit" or commands[0] == "ex": # unlike quit, this includes saving
                            open(last_saved, "w", encoding='utf-8').write("\n".join(lines))
                        else:
                            if not canvas.bool_query("Are you sure you don't want to save? "):
                                open(last_saved, "w", encoding='utf-8').write("\n".join(lines))
                        running = False
                    case "write" | "w":
                        open(commands[1], "w", encoding='utf-8').write("\n".join(lines))
                        last_saved = commands[1]
                    case "save" | "s":
                        if last_saved == None:
                            canvas.message(f"No file to save to. Use 'write [filename]'.")
                        else:
                            open(last_saved, "w", encoding='utf-8').write("\n".join(lines))
                    case "read" | "r" | "open" | "get":
                        lines = open(commands[1], "r", encoding='utf-8').readlines()
                        for i, line in enumerate(lines):
                            lines[i] = line.replace("\n", "").replace("\t", "    ")
                        last_saved = commands[1]
                    case "mount" | "dir" | "cd" | "chdir":
                        os.chdir(commands[1])
                    case "cwd":
                        canvas.message(f"cwd: {os.getcwd()}")
                    case "fs" | "filesystem" | "files":
                        filename = filesystem_selector.take(canvas)
                        lines = open(filename, "r", encoding='utf-8').readlines()
                        for i, line in enumerate(lines):
                            lines[i] = line.replace("\n", "").replace("\t", "    ")
                        last_saved = filename
                    case _:
                        canvas.message("That's not a command!", color=(255, 0, 0))

        case _:
            cursor_blink = time.time()
            apply_quickfixes()
            current_line = lines[position[1]]
            pressed_key = pressed_key.replace("\t", "    ")
            if pressed_key == "\b":
                if position[0] == 0:
                    position[0] = len(lines[position[1]-1]) - 1
                    if position[1] != 0:
                        lines[position[1]-1] += lines.pop(position[1])
                        position[1] -= 1
                else:    
                    lines[position[1]] = current_line[0:position[0] - 1] + current_line[position[0]:len(current_line)]
                    position[0] -= 2
            else:
                lines[position[1]] = current_line[0:position[0]] + pressed_key + current_line[position[0]:len(current_line)]
            position[0] += len(pressed_key)
    apply_quickfixes()
    canvas.clear()

    for i, line in enumerate(lines):
        index_text = f" {i} "
        canvas.put((0, i), index_text, color=(188, 248, 236))
        
        # line_highlight = (12, 116, 137)
        # if line.startswith("//") or line.startswith("#"):
        #     line_highlight = (209, 96, 61)

        tokens = syntax.LexicalAnalyzer().lex(line)
        offset = len(f" {len(lines)} ")
        is_comment = False
        for ti, token in enumerate(tokens):
            # canvas.put((offset, i), line, color=line_highlight)
            if token.text == "#" or (token.text == "/" and len(tokens) > ti+1 and tokens[ti+1].text == "/"):
                is_comment = True
            if token.data_type != "whitespace":
                expected_color = color_table["comment"] if is_comment else color_table[token.data_type]
                if token.text in special_colorizations:
                    expected_color = special_colorizations[token.text]
                
                canvas.put((offset, i), token.text, color=expected_color)
                
                if "string" in token.data_type and not is_comment:
                    indexes = find_all_indexes(token.text, "\\")
                    for backslash_index in indexes:
                        canvas.put((offset+backslash_index, i), "\\", color=color_table["escapes"])
                    # token.text = token.text.replace("\\", f"{tui.rgb_ansi((173, 50, 31))}\\")
            offset += len(token.text)

    shift = len(f" {len(lines)} ")
    if round((time.time() - cursor_blink) * 2) % 2 == 0:
        canvas.plot(position[0] + shift, position[1], fill="|")
    center_y = (position[1] + round(canvas.size[1] / 2))
    canvas.move((canvas.size[0] - position[0] - shift - 5 if (position[0] + shift) > canvas.size[0] else 0, canvas.size[1] - center_y if center_y > canvas.size[1] else 0))
    canvas.put((0, canvas.size[1] - 1), f"Lines: {len(lines)}, {"unsaved" if last_saved == None else last_saved} | ATE v2.2.0 {' ' * canvas.size[0]}", color=(227, 193, 111))
    canvas.print()

time.sleep(1)