from asec.graphics.pixel import Pixel
from asec.graphics.screen import Screen as DefaultScreen


class Screen(DefaultScreen):
    def __init__(self, gpu):
        self._gpu = gpu
        super(Screen, self).__init__(160, 144)



