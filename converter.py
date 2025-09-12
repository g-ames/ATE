import tgfx

converter = tgfx.ImageConverter()

down_scale = 1

converter.size = (round(100 * down_scale), round(50 * down_scale))
converter.character_gradient = "█"
converter.return_text = True

def convert_image(path):
    return converter.convert_image_file(path).as_text

# open("daddt.jpg.txt", "w", encoding="utf-8").write(converter.convert_image_file("daddt.jpg").as_text)