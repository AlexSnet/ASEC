import logging


class Keyboard(object):

    KEYMAP = {
        'UP': 38,
        'DOWN': 40,
        'LEFT': 37,
        'RIGHT': 39,

        'A': 65,
        'B': 83,

        'START': 13,
        'SELECT': 32
    }

    def __init__(self, mainboard):
        self.mainboard = mainboard
        self.keys = None
        self.colidX = None
        self.reset()

    def reset(self):
        self.keys = {0: 0x0F, 1: 0x0F}
        self.colidX = 0

    def writeByte(self, value):
        self.colidX = value & 0x30

    def readByte(self):
        if self.colidX == 0x00:
            return 0x00
        elif self.colidX == 0x10:
            return self.keys[0]
        elif self.colidX == 0x20:
            return self.keys[1]
        else:
            return 0x00

    def press(self, keyCode):
        if keyCode == Keyboard.KEYMAP['UP']:
            self.keys[1] &= 0xB
        elif keyCode == Keyboard.KEYMAP['DOWN']:
            self.keys[1] &= 0x7
        elif keyCode == Keyboard.KEYMAP['LEFT']:
            self.keys[1] &= 0xD
        elif keyCode == Keyboard.KEYMAP['RIGHT']:
            self.keys[1] &= 0xE

        elif keyCode == Keyboard.KEYMAP['A']:
            self.keys[0] &= 0xE
        elif keyCode == Keyboard.KEYMAP['B']:
            self.keys[0] &= 0xD

        elif keyCode == Keyboard.KEYMAP['START']:
            self.keys[0] &= 0x7
        elif keyCode == Keyboard.KEYMAP['SELECT']:
            self.keys[0] &= 0xB

    def release(self, keyCode):
        if keyCode == Keyboard.KEYMAP['UP']:
            self.keys[1] |= 0x4
        elif keyCode == Keyboard.KEYMAP['DOWN']:
            self.keys[1] |= 0x8
        elif keyCode == Keyboard.KEYMAP['LEFT']:
            self.keys[1] |= 0x2
        elif keyCode == Keyboard.KEYMAP['RIGHT']:
            self.keys[1] |= 0x1

        elif keyCode == Keyboard.KEYMAP['A']:
            self.keys[0] |= 0x1
        elif keyCode == Keyboard.KEYMAP['B']:
            self.keys[0] |= 0x2

        elif keyCode == Keyboard.KEYMAP['SELECT']:
            self.keys[0] |= 0x4
        elif keyCode == Keyboard.KEYMAP['START']:
            self.keys[0] |= 0x8
