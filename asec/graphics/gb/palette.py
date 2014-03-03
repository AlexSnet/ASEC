class Palette:
    def __init__(self):
        self.bg = {}
        self.obj0 = {}
        self.obj1 = {}

        self.reset()

    def reset(self):
        for i in range(4):
            self.bg[i] = self.obj0[i] = self.obj1[i] = 0xFF
