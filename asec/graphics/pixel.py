def clamp(x):
    return max(0, min(x, 255))

_NUMERALS = '0123456789abcdefABCDEF'
_HEXDEC = {v: int(v, 16) for v in (x+y for x in _NUMERALS for y in _NUMERALS)}


class Pixel(object):
    def __init__(self, red=0, green=0, blue=0):
        self._r = self._g = self._b = 0

        self.red = red
        self.green = green
        self.blue = blue

    def __repr__(self):
        return '<Pixel: %x>' % self.hex

    def __hex__(self):
        color = self.red
        color = (color << 8) + self.green
        color = (color << 8) + self.blue
        return color

    @property
    def hex(self):
        return self.__hex__()

    @hex.setter
    def hex(self, value):
        if type(value) == int or value.isnumeric():
            value = '%x' % int(value)
        elif value[0] == '#':
            value = value[1:]
        elif len(value) == 8 and value[0:2].lower() == '0x':
            value = value[2:]

        self.red, self.green, self.blue = (
            _HEXDEC[value[0:2]], _HEXDEC[value[2:4]], _HEXDEC[value[4:6]]
        )

    @property
    def red(self):
        return self._r

    @red.setter
    def red(self, value):
        self._r = clamp(value)

    @property
    def green(self):
        return self._g

    @green.setter
    def green(self, value):
        self._g = clamp(value)

    @property
    def blue(self):
        return self._b

    @blue.setter
    def blue(self, value):
        self._b = clamp(value)
