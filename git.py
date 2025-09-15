def pretick(_, _):    pass
def posttick(canvas, globs):
    if not globs["__SIDEBAR__"]:
        quit("Sidebar not loaded!")