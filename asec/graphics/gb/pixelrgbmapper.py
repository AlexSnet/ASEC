from asec.graphics.pixel import Pixel

class PixelRGBMapper:
    def __init__(self):
        self.OFF = Pixel(255, 255, 255)
        self.LO = Pixel(192, 192, 192)
        self.HI = Pixel(96, 96, 96)
        self.ON = Pixel(0, 0, 0)

    def map(self, percent):
        if percent == 0:
            return self.OFF
        elif percent == 33:
            return self.LO
        elif percent == 66:
            return self.HI
        elif percent == 1:
            return self.ON
        else:
            return self.OFF
