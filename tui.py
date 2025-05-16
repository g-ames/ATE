_print = print

import tgfx

canvas = tgfx.Canvas()

class Vector2():
    def __init__(self, x, y):
        self.x = 0 if x == None else x
        self.y = 0 if y == None else y

class Dim():
    def __init__(self, x, y, percent_x, percent_y):
        self.pixels = Vector2(x, y)
        self.percents = Vector2(percent_x, percent_y)
    def vectorize(self):
        _print(self.percents.x, self.percents.y, self.percents.x * canvas.size[0], self.percents.y * canvas.size[1])
        quit()
        return Vector2(self.pixels.x + (self.percents.x * canvas.size[0]), self.pixels.y + (self.percents.y * canvas.size[1]))

class UIElement():
    def __init__(self, position, size):
        self.position = position
        self.size = size
        self.fill = "█"
        self.color = (128, 128, 128)
        self.children = []
    def append_child(self, child):
        self.children.append(child)
    def render(self, offset=Vector2(0,0)): 
        vectorized_position = self.position.vectorize()
    
        vectorized_position.x += offset.x
        vectorized_position.y += offset.y
        
        vectorized_size = self.size.vectorize()

        canvas.message(f"""
            {vectorized_position.x}, 
            {vectorized_position.y}, 
            {vectorized_size.x}, 
            {vectorized_size.y}, 
            {self.fill},
            {self.color}""")

        canvas.rect(
            vectorized_position.x, 
            vectorized_position.y, 
            vectorized_size.x, 
            vectorized_size.y, 
            fill=self.fill,
            color=self.color
        )

        for child in self.children:
            child.render(vectorized_position)

root = UIElement(Dim(0, 0, 0, 0), Dim(0, 1, 0, 1))

def print():
    tgfx.hide_cursor()
    canvas.clear()
    root.render()
    canvas.print()
