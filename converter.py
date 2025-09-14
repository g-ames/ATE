import tgfx

converter = tgfx.ImageConverter()

converter.character_gradient = "█"
converter.return_text = True

def convert_image(path):
    converter.size = tgfx.get_terminal_size()
    converter.size = (converter.size[0], converter.size[1] * 2) # because characters are taller than they are wide
    return converter.convert_image_file(path).as_text

def view_image(path):
    print(convert_image(path))

    tgfx.getkey(blocking=True)
    print("\n" * tgfx.get_terminal_size()[1])

# open("daddt.jpg.txt", "w", encoding="utf-8").write(converter.convert_image_file("daddt.jpg").as_text)