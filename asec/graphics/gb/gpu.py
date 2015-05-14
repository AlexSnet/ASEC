import logging

from collections import defaultdict

from asec.memory.ram import RAM

from asec.graphics.gb.palette import Palette
from asec.graphics.gb.pixelrgbmapper import PixelRGBMapper
from asec.graphics.gb.screen import Screen
from asec.utils.signal import Signal


class GPU(object):
    """
    GameBoy graphics processor unit
    """

    def __init__(self, mainboard):
        self.mainboard = mainboard
        self.log = logging.getLogger(self.__class__.__name__)

        self.screen = Screen(self)

        self.VRAM = RAM(0x2000)
        self.ORAM = RAM(0xA0)

        self._reg = {}

        self.rgbMapper = PixelRGBMapper()
        self.palette = Palette()

        self.tilemap = {}  # [512][8][8]

        self._curline = 0
        self._curscan = 0
        self._linemode = 0
        self._modeclocks = 0
        self._yscrl = 0
        self._xscrl = 0
        self._raster = 0
        self._ints = 0

        self._lcdon = 0
        self._bgon = 0
        self._objon = 0
        self._winon = 0

        self._objsize = 0
        self._scanrow = None
        self._objdata = None
        self._tilemap = None

        self._bgtilebase = 0x0000
        self._bgmapbase = 0x1800
        self._wintilebase = 0x1800

        self.renderScreen = Signal()

        self.reset()

    def reset(self):
        self._curline = 0
        self._curscan = 0
        self._linemode = 0
        self._modeclocks = 0
        self._yscrl = 0
        self._xscrl = 0
        self._raster = 0
        self._ints = 0

        self._lcdon = 0
        self._bgon = 0
        self._objon = 0
        self._winon = 0

        self._objsize = 0
        self._scanrow = dict([(i, 0) for i in range(160)])
        self._objdata = dict([(i, {'y': -16,'x': -8,'tile': 0,'palette': 0,'yflip': 0,'xflip': 0,'prio': 0,'num': i}) for i in range(40)])
        self._tilemap = defaultdict(lambda:{'x':0, 'y':0})

        self._bgtilebase = 0x0000
        self._bgmapbase = 0x1800
        self._wintilebase = 0x1800

        self.VRAM.reset()
        self.ORAM.reset()
        self.palette.reset()

        self.screen.reset()

        # Cleaning tilemap
        for i in range(512):
            self.tilemap[i] = {}
            for y in range(8):
                self.tilemap[i][y] = {}
                for x in range(8):
                    self.tilemap[i][y][x] = 0

        #self.renderScreen(self.screen)
        self.log.debug('reset')

    def checkline(self):
        self._modeclocks += self.mainboard.CPU.R.m

        # @TODO: Remove this!
        # For debug only
        # self.renderScreen(self.screen)

        if self._linemode == 0:  # In hblank
            if self._modeclocks >= 51:
                # End of hblank for last scanline; render screen
                if self._curline == 143:
                    self._linemode = 1
                    self.log.debug('Render screen')
                    self.renderScreen(self.screen)
                    self.mainboard.MMU.IF |= 1
                else:
                    self._linemode = 2

                self._curline += 1
                self._curscan += 640
                self._modeclocks = 0

        elif self._linemode == 1:  # In vblank
            if self._modeclocks >= 114:
                self._modeclocks = 0
                self._curline += 1

                if self._curline == 153:
                    self._curline = 0
                    self._curscan = 0
                    self._linemode = 2

        elif self._linemode == 2:  # In OAM-read mode
            if self._modeclocks >= 20:
                self._modeclocks = 0
                self._linemode = 3

        elif self._linemode == 3:  # In VRAM-read mode
            # Render scanline at end of allotted time
            if self._modeclocks >= 43:
                self._modeclocks = 0
                self._linemode = 0

                if self._lcdon:
                    if self._bgon:
                        linebase = self._curscan
                        mapbase = self._bgmapbase + ((((self._curline + self._yscrl) & 255) >> 3) << 5)
                        y = (self._curline + self._yscrl) & 7
                        x = self._xscrl & 7
                        t = (self._xscrl >> 3) & 31
                        w = 160

                        if self._bgtilebase:
                            tile = self.VRAM.readByte(mapbase + t)
                            if tile < 128:
                                tile += 256

                            tilerow = self._tilemap[tile][y]
                            while w:
                                self._scanrow[160 - x] = tilerow[x]
                                self.screen._pixels[linebase + 3] = self.palette.bg[tilerow[x]]

                                x += 1

                                if x == 8:
                                    t = (t + 1) & 31
                                    x = 0
                                    tile = self.VRAM.readByte(mapbase + t)
                                    if tile < 128:
                                        tile += 256
                                    tilerow = self._tilemap[tile][y]

                                linebase += 4
                                w -= 1
                        else:
                            tilerow = self._tilemap[self.VRAM.readByte(mapbase + t)][y]
                            while w:
                                self._scanrow[160 - x] = tilerow[x]
                                self.screen._pixels[linebase + 3] = self.palette.bg[tilerow[x]]

                                x += 1

                                if x == 8:
                                    t = (t + 1) & 31
                                    x = 0
                                    tilerow = self._tilemap[self.VRAM.readByte(mapbase + t)][y]

                                linebase += 4
                                w -= 1

                    if self._objon:
                        cnt = 0
                        if self._objsize:
                            for i in range(40):
                                # What do i do here?
                                pass
                        else:
                            linebase = self._curscan
                            for i in range(40):
                                obj = self._objdata[i]
                                if obj['y'] <= self._curline and (obj['y'] + 8) > self._curline:
                                    if obj['yflip']:
                                        tilerow = self._tilemap[obj['tile']][7 - (self._curline - obj['y'])]
                                    else:
                                        tilerow = self._tilemap[obj['tile']][self._curline - obj['y']]

                                    if obj['palette']:
                                        pal = self.palette.obj1
                                    else:
                                        pal = self.palette.obj0

                                    linebase = (self._curline * 160 + obj['x']) * 4
                                    if obj['xflip']:
                                        for x in range(8):
                                            if obj['x'] + x >= 0 and obj['x'] + x < 160:
                                                if tilerow[7 - x] and (obj['prio'] or not self._scanrow[x]):
                                                    self.screen._pixels[linebase + 3] = pal[tilerow[7 - x]]

                                            linebase += 4
                                    else:
                                        for x in range(8):
                                            if obj['x'] + x >= 0 and obj['x'] + x < 160:
                                                if tilerow[x] and (obj['prio'] or not self._scanrow[x]):
                                                    self.screen._pixels[linebase + 3] = pal[tilerow[x]]

                                            linebase += 4

                                    cnt += 1
                                    if cnt > 10:
                                        break

    def updateTile(self, address, value):
        saddr = address
        if address & 1:
            saddr -= 1
            address -= 1

        tile = (address >> 4) & 511
        y = (address >> 1) & 7

        self.log.debug('updateTile', address, value, tile, y, saddr)

        for x in range(8):
            sx = 1 << (7 - x)
            self.tilemap[tile][y][x] = 2 if (1 if self.VRAM.readByte(saddr) & sx else 0) | (self.VRAM.readByte(saddr + 1) & sx) else 0

    def updateORAM(self, address, value):
        address -= 0xFE00
        obj = address >> 2
        if obj < 40:
            adr = address & 3
            if adr == 0:
                self._objdata[obj]['y'] = value - 16
            elif adr == 1:
                self._objdata[obj]['x'] = value - 8
            elif adr == 2:
                if self._objsize:
                    self._objdata[obj]['tile'] = value & 0xFE
                else:
                    self._objdata[obj]['tile'] = value
            elif adr == 3:
                self._objdata[obj]['palette'] = 1 if value & 0x10 else 0
                self._objdata[obj]['xflip'] = 1 if value & 0x20 else 0
                self._objdata[obj]['yflip'] = 1 if value & 0x40 else 0
                self._objdata[obj]['prio'] = 1 if value & 0x80 else 0
        print(self._objdata[obj])
        # self._objdatasorted = sorted(self._objdata, lambda x: x['x'])

    def readByte(self, address):
        gaddr = address - 0xFF40
        if gaddr == 0:
            return (0x80 if self._lcdon else 0) | \
                   (0x10 if self._bgtilebase == 0x0000 else 0) | \
                   (0x08 if self._bgmapbase == 0x1C00 else 0) | \
                   (0x04 if self._objsize else 0) | \
                   (0x02 if self._objon else 0) | \
                   (0x01 if self._bgon else 0)
        elif gaddr == 1:
            return (4 if self._curline == self._raster else 0) | self._linemode
        elif gaddr == 2:
            return self._yscrl
        elif gaddr == 3:
            return self._xscrl
        elif gaddr == 4:
            return self._curline
        elif gaddr == 5:
            return self._raster
        else:
            return self._reg[gaddr]

    def writeByte(self, address, value):
        self.log.debug('writeByte', address, value)
        gaddr = address - 0xFF40
        self._reg[gaddr] = value

        if gaddr == 0:
            self._lcdon = 1 if value & 0x80 else 0
            self._bgtilebase = 0x0000 if value & 0x10 else 0x0800
            self._bgmapbase = 0x1C00 if value & 0x08 else 0x1800
            self._objsize = 1 if value & 0x04 else 0
            self._objon = 1 if value & 0x02 else 0
            self._bgon = 1 if value & 0x01 else 0

        elif gaddr == 2:
            self._yscrl = value

        elif gaddr == 3:
            self._xscrl = value

        elif gaddr == 5:
            self._raster = value

        # OAM DMA
        elif gaddr == 6:
            for i in range(160):
                v = self.readByte((value << 8) + i)
                self.log.debug('WriteByte ORAM DMA', i, v)
                self.ORAM.writeByte(i, v)
                self.updateORAM(0xFE00 + i, v)

        # BG palette mapping
        elif gaddr == 7:
            for i in range(4):
                z = (value >> (i * 2)) & 3
                if z == 0:
                    self.palette.bg[i] = 255
                elif z == 1:
                    self.palette.bg[i] = 192
                elif z == 2:
                    self.palette.bg[i] = 96
                elif z == 3:
                    self.palette.bg[i] = 0

        # OBJ0 palette mapping
        elif gaddr == 8:
            for i in range(4):
                z = (value >> (i * 2)) & 3
                if z == 0:
                    self.palette.obj0[i] = 255
                elif z == 1:
                    self.palette.obj0[i] = 192
                elif z == 2:
                    self.palette.obj0[i] = 96
                elif z == 3:
                    self.palette.obj0[i] = 0

        # OBJ1 palette mapping
        elif gaddr == 9:
            for i in range(4):
                z = (value >> (i * 2)) & 3
                if z == 0:
                    self.palette.obj1[i] = 255
                elif z == 1:
                    self.palette.obj1[i] = 192
                elif z == 2:
                    self.palette.obj1[i] = 96
                elif z == 3:
                    self.palette.obj1[i] = 0
