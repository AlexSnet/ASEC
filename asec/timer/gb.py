import logging

class Clock:
    def __init__(self):
        self.main = 0
        self.sub = 0
        self.div = 0

    def reset(self):
        self.main = 0
        self.sub = 0
        self.div = 0


class Timer:
    def __init__(self, mainboard):
        self.mainboard = mainboard
        self.log = logging.getLogger(self.__class__.__name__)

        self.div = 0
        self.tma = 0
        self.tima = 0
        self.tac = 0

        self.clock = Clock()
        self.reset()

    def reset(self):
        self.div = 0
        self.tma = 0
        self.tima = 0
        self.tac = 0
        self.clock.reset()
        self.log.debug('reset')

    def inc(self):
        oldclock = self.clock.main

        self.clock.sub += self.mainboard.CPU.R.m
        if self.clock.sub > 3:
            self.clock.main += 1
            self.clock.sub -= 4

            self.clock.div += 1
            if self.clock.div == 16:
                self.clock.div = 0
                self.div += 1
                self.div &= 255

        if self.tac & 4:
            tac3 = self.tac & 3
            if tac3 == 0:
                if self.clock.main >= 64:
                    self.step()
            elif tac3 == 1:
                if self.clock.main >= 1:
                    self.step()
            elif tac3 == 2:
                if self.clock.main >= 4:
                    self.step()
            elif tac3 == 3:
                if self.clock.main >= 16:
                    self.step()

    def step(self):
        self.tima += 1
        self.clock.main = 0

        if self.tima > 255:
            self.tima = self.tma
            self.mainboard.MMU.IF |= 4

    def readByte(self, address):
        if address == 0xFF04:
            return self.div
        elif address == 0xFF05:
            return self.tima
        elif address == 0xFF06:
            return self.tma
        elif address == 0xFF07:
            return self.tac

    def writeByte(self, address, value):
        if address == 0xFF04:
            self.div = value
        elif address == 0xFF05:
            self.tima = value
        elif address == 0xFF06:
            self.tma = value
        elif address == 0xFF07:
            self.tac = value
