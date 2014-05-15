import time

from asec.device import Mainboard
from asec.memory.mmu.gb import MMU
from asec.processor.z80 import Processor
from asec.graphics.gb.gpu import GPU
from asec.input.gb.keyboard import Keyboard
from asec.timer.gb import Timer

class Device(Mainboard):
    def __init__(self):
        super(Device, self).__init__()

        self.name = 'GameBoy'

        self._loop = True

        self.CPU = Processor(self)
        self.MMU = MMU(self)
        self.GPU = GPU(self)
        self.KEY = Keyboard(self)
        self.TIMER = Timer(self)

    def reset(self):
        self.MMU.reset()
        self.GPU.reset()
        self.CPU.reset()
        self.KEY.reset()
        self.TIMER.reset()
        self.log.debug('reset')

    def insertCartridge(self, filePath):
        self.log.debug('Cartridge inserted "%s".' % filePath)
        if self._started.is_set():
            self._stop()
        self.reset()
        self.MMU.loadROM(filePath)
        # self.start()

    def frame(self):
        fclock = self.CPU.CLOCK.m+17556
        # self.log.debug("Frame")
        if self.CPU._HALT:
            self.CPU.R.m = 1
        else:
            instruction = self.MMU.readByte(self.CPU.R.pc)
            self.CPU.call(instruction)
            self.CPU.R.pc += 1
            self.CPU.R.pc &= 65535

        if self.CPU.R.ime and self.MMU.IE and self.MMU.IF:
            self.CPU._HALT = 0
            self.CPU.R.ime = 0
            ifired = self.MMU.IE & self.MMU.IF
            if ifired & 1:
                self.MMU.IF &= 0xFE
                self.CPU.RST40()
            elif ifired & 2:
                self.MMU.IF &= 0xFD
                self.CPU.RST48()
            elif ifired & 4:
                self.MMU.IF &= 0xFB
                self.CPU.RST50()
            elif ifired & 8:
                self.MMU.IF &= 0xF7
                self.CPU.RST58()
            elif ifired & 16:
                self.MMU.IF &= 0xEF
                self.CPU.RST60()
            else:
                self.CPU.R.ime = 1

        self.CPU.CLOCK.m += self.CPU.R.m
        self.GPU.checkline()
        self.TIMER.inc()

        if self.CPU.CLOCK.m >= fclock:
            self.CPU._STOP = 1

    def run(self):
        self.log.debug('Execution loop started')
        self.CPU._STOP = 0
        while self._loop:
            if self.CPU._STOP == 0:
                #self.frame()
                self.CPU.exec()
                # time.sleep(.016)
        self.log.debug('Execution loop ended')

    def play(self):
        self.CPU._STOP = 0

    def pause(self):
        self.CPU._STOP = 1

if __name__ == '__main__':
    import sys
    import logging
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)-15s\t%(levelname)-10s\t%(name)-20s\t%(process)-5d\t%(message)s")

    cartridge = ''
    if len(sys.argv) == 2:
        cartridge = sys.argv[1]
    else:
        cartridge = '../../roms/ttt.gb'

    gb = Device()
    gb.insertCartridge(cartridge)
    gb.start()