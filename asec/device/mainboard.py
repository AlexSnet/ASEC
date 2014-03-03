import logging
from threading import Thread

class Mainboard(Thread):
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

        self.ERAM = None

        self.BIOS = None

        self.RAM = None
        self.ROM = None

        self.CPU = None

        super(Mainboard, self).__init__()




