import os
import logging

from asec.memory.ram import RAM
from asec.memory.rom import ROM
from asec.bios.gb import BIOS


class MMU:
    """
    Memory Management Unit for GB
    """

    # [0000-3FFF] Cartridge ROM, bank 0: The first 16,384 bytes of the
    # cartridge program are always available at this point in the memory map.
    #
    # Special circumstances apply: [0000-00FF] BIOS: When the CPU starts up, PC
    # starts at 0000h, which is the start of the 256-byte GameBoy BIOS code.
    # Once the BIOS has run, it is removed from the memory map, and this area
    # of the cartridge rom becomes addressable. [0100-014F] Cartridge header:
    # This section of the cartridge contains data about its name and
    # manufacturer, and must be written in a specific format.
    ROM_BANK_0_OFFSET = 0x0000
    ROM_BANK_0_END = 0x3FFF

    BIOS_OFFSET = 0x0000
    BIOS_END = 0x00FF

    CARTRIDGE_HEADER_OFFSET = 0x0100
    CARTRIDGE_HEADER_END = 0x014F

    # [4000-7FFF] Cartridge ROM, other banks: Any subsequent 16k "banks" of the
    # cartridge program can be made available to the CPU here, one by one a
    # chip on the cartridge is generally used to switch between banks, and make
    # a particular area accessible. The smallest programs are 32k, which means
    # that no bank-selection chip is required.
    ROM_BANK_1_OFFSET = 0x4000
    ROM_BANK_1_END = 0x7FFF

    # [8000-9FFF] Graphics RAM: Data required for the backgrounds and sprites
    # used by the graphics subsystem is held here, and can be changed by the
    # cartridge program. This region will be examined in further detail in part
    # 3 of this series.
    #
    # [8000-87FF] Tile set #1: tiles 0-127 [8800-8FFF] Tile set #1: tiles
    # 128-255 Tile set #0: tiles -1 to -128 [9000-97FF] Tile set #0: tiles
    # 0-127 [9800-9BFF] Tile map #0 [9C00-9FFF] Tile map #1
    GPU_VRAM_OFFSET = 0x8000
    GPU_VRAM_END = 0x9FFF

    # [A000-BFFF] Cartridge (External) RAM: There is a small amount of
    # writeable memory available in the GameBoy if a game is produced that
    # requires more RAM than is available in the hardware, additional 8k chunks
    # of RAM can be made addressable here.
    EXT_RAM_OFFSET = 0xA000
    EXT_RAM_END = 0xBFFF

    # [C000-DFFF] Working RAM: The GameBoy's internal 8k of RAM, which can be
    # read from or written to by the CPU.
    WORKING_RAM_OFFSET = 0xC000
    WORKING_RAM_END = 0xDFFF

    # [E000-FDFF] Working RAM (shadow): Due to the wiring of the GameBoy
    # hardware, an exact copy of the working RAM is available 8k higher in the
    # memory map. This copy is available up until the last 512 bytes of the
    # map, where other areas are brought into access.
    WORKING_RAM_SHADOW_OFFSET = 0xE000
    WORKING_RAM_SHADOW_END = 0xFDFF

    # [FE00-FE9F] Graphics: sprite information: Data about the sprites rendered
    # by the graphics chip are held here, including the sprites' positions and
    # attributes.
    GRAPHICS_SPRITE_OFFSET = 0xFE00
    GRAPHICS_SPRITE_END = 0xFE9F

    # [FF00-FF7F] Memory-mapped I/O: Each of the GameBoy's subsystems
    # (graphics, sound, etc.) has control values, to allow programs to create
    # effects and use the hardware. These values are available to the CPU
    # directly on the address bus, in this area.
    MEM_MAPPED_IO_OFFSET = 0xFF00
    MEM_MAPPED_IO_END = 0xFF7F

    # [FF80-FFFF] Zero-page RAM: A high-speed area of 128 bytes of RAM is
    # available at the top of memory. Oddly, though this is "page" 255 of the
    # memory, it is referred to as page zero, since most of the interaction
    # between the program and the GameBoy hardware occurs through use of this
    # page of memory.
    ZERO_PAGE_RAM_OFFSET = 0xFF80
    ZERO_PAGE_RAM_END = 0xFFFF

    def __init__(self, mainboard):
        self._mainboard = mainboard

        self.log = logging.getLogger(self.__class__.__name__)

        self.BIOS = BIOS()
        self.ROM = ROM(0x100000)

        self.ERAM = RAM(0x8000)
        self.WRAM = RAM(0x2000)
        self.ZRAM = RAM(0x80)

        self.cartType = 0

        self.romBank = 0
        self.ramBank = 0
        self.ramOn = 0
        self.mode = 0

        self.romOffs = 0x4000
        self.ramOffs = 0

        self.inBios = 1
        self.IE = 0
        self.IF = 0  # Interrupt flags

        self.reset()

    def reset(self):
        self.inBios = 1
        self.IE = 0
        self.IF = 0
        self.cartType = 0
        self.romBank = 0
        self.ramBank = 0
        self.ramOn = 0
        self.mode = 0
        self.romOffs = 0x4000
        self.ramOffs = 0x00

        self.BIOS.reset()
        self.ROM.reset(fill=False)
        self.ERAM.reset()
        self.WRAM.reset()
        self.ZRAM.reset()
        self.log.debug('reset')

    def readByte(self, address):
        """
        reads byte
        @param address int
        @return int
        """
        value = self._readByte(address)
        self.log.debug("[0x%06X] >> 0x%06X", address, value)
        return value

    def _readByte(self, address):
        adr = address & 0xF000

        self.log.debug(
            'Reading byte from 0x%04X & 0xF000 = 0x%04X',
            address,
            adr
        )

        # ROM Bank 0
        if adr == 0x0000:
            if self.inBios:
                self.log.debug('In section: BIOS')
                if address < 0x0100:
                    return self.BIOS.readByte(address)
                elif self._mainboard.CPU.R.pc == 0x0100:
                    self.log.debug('In section: BIOS (leaving)')
                    self.inBios = False
                    return 0x0
            else:
                self.log.debug('In section: ROM')
                return self.ROM.readByte(address)

        elif 0x1000 <= adr <= 0x3000:
            self.log.debug('In section: ROM')
            return self.ROM.readByte(address)

        # ROM Bank 1
        elif 0x4000 <= adr <= 0x7000:
            self.log.debug('In section: ROM Bank 1')
            return self.ROM.readByte(self.romOffs + (address & 0x3FFF))

        # VRAM
        elif 0x8000 <= adr <= 0x9000:
            self.log.debug('In section: VRAM')
            return self._mainboard.GPU.VRAM.readByte(address & 0x1FFF)

        # External RAM
        elif 0xA000 <= adr <= 0xB000:
            self.log.debug('In section: External RAM')
            return self.ERAM.readByte(self.ramOffs + (address & 0x1FFF))

        # Work RAM and echo
        elif 0xC000 <= adr <= 0xE000:
            self.log.debug('In section: Work RAM & echo')
            return self.WRAM.readByte(address & 0x1FFF)

        else:
            adr = address & 0x0F00
            self.log.debug('in section 0xF000 with adr=0x%04X', adr)
            # Echo RAM
            if 0x000 <= adr <= 0xD00:
                self.log.debug('In section: Echo RAM')
                return self.WRAM.readByte(address & 0x1FFF)

            # OAM
            elif adr == 0xE00:
                self.log.debug('In section: OAM')
                return self._mainboard.GPU.ORAM.readByte(address & 0xFF) \
                    if (address & 0xFF) < 0xA0 else 0

            # Zeropage RAM, I/O, interrupts
            else:
                self.log.debug('In section: Zeropage RAM, I/O, interrupts')
                if address == 0xFFFF:
                    self.log.debug('In section: 0xFFFF, IE')
                    return self.IE

                elif address > 0xFF7F:
                    self.log.debug('In section: Zeropage RAM')
                    return self.ZRAM.readByte(address & 0x7F)

                else:
                    adr = address & 0xF0
                    if adr == 0x00:
                        adr = address & 0xF

                        if adr == 0:
                            self.log.debug('In section: Keyboard')
                            return self._mainboard.KEY.readByte()

                        elif 4 <= adr <= 7:
                            self.log.debug('In section: Timer')
                            return self._mainboard.TIMER.readByte(address)

                        elif adr == 15:
                            self.log.debug('In section: Interrupt')
                            return self.IF  # interrupt flags

                        else:
                            self.log.debug('In section: 0')
                            return 0

                    elif 0x10 <= adr <= 0x30:
                        self.log.debug('In section: 0')
                        return 0

                    elif 0x40 <= adr <= 0x70:
                        self.log.debug('In section: GPU')
                        return self._mainboard.GPU.readByte(address)

                    else:
                        self.log.error(
                            'Unknown section, address = 0x%04X',
                            address
                        )

    def readWord(self, address):
        """
        reads a word, 16-bit
        @param address int
        @return int
        """
        return self.readByte(address) + self.readByte(address + 1) << 8

    def writeByte(self, address, value):
        """
        @param address int
        @param value int
        """
        self.log.debug("[0x%06X] << 0x%06X", address, value)
        adr = address & 0xF000

        # ROM bank 0
        # MBC1: Turn external RAM on
        if 0x0000 <= adr <= 0x1000:
            if self.cartType == 1:
                self.ramOn = 1 if (value & 0xF) == 0xA else 0

        elif 0x2000 <= adr <= 0x3000:
            if self.cartType == 1:
                self.romBank &= 0x60
                value &= 0x1F
                value = value or 1
                self.romBank |= value
                self.romOffs = self.romBank * 0x4000

        # ROM bank 1
        # MBC1: RAM bank switch
        elif 0x4000 <= adr <= 0x5000:
            if self.cartType == 1:
                if self.mode > 0:
                    self.ramBank = value & 3
                    self.ramOffs = self.ramBank * 0x2000
                else:
                    self.romBank &= 0x1F
                    self.romBank |= ((value & 3) << 5)
                    self.romOffs = self.romBank * 0x4000

        elif 0x6000 <= adr <= 0x7000:
            if self.cartType == 1:
                self.mode = value & 1

        # VRAM
        elif 0x8000 <= adr <= 0x9000:
            self._mainboard.GPU.VRAM.writeByte(
                self.ramOffs + (address & 0x1FFF),
                value
            )

        # Extrnal RAM
        elif 0xA000 <= adr <= 0xB000:
            self.ERAM.writeByte(address & 0x1FFF, value)

        # Work RAM and echo
        elif 0xC000 <= adr <= 0xE000:
            self.WRAM.writeByte(address & 0x1FFF, value)

        else:
            adr = address & 0x0F00

            # Echo RAM
            if 0x000 <= adr <= 0xD00:
                self.WRAM.writeByte(address & 0x1FFF, value)

            # 0AM
            elif adr == 0xE00:
                if (address & 0xFF) < 0xA0:
                    self._mainboard.GPU.ORAM.writeByte(address & 0xFF, value)
                    self._mainboard.GPU.updateORAM(address, value)

            # Zeropage RAM, I/O
            elif adr == 0xF00:
                if address == 0xFFFF:
                    self.IE = value

                elif address > 0xFF7F:
                    self.ZRAM.writeByte(address & 0x7F, value)

                else:
                    adr = address & 0xF0

                    if adr == 0x00:
                        adr = address & 0xF
                        if adr == 0:
                            self._mainboard.KEY.writeByte(value)

                        elif 4 <= adr <= 7:
                            self._mainboard.TIMER.writeByte(address, value)

                        elif adr == 15:
                            self.IF = value

                    elif 0x10 <= adr <= 0x30:
                        return

                    elif 0x40 <= adr <= 0x70:
                        self._mainboard.GPU.writeByte(address, value)

    def writeWord(self, address, value):
        """
        @param address int
        @param value int
        """
        self.writeByte(address, value & 0xFF)
        # self.writeByte(address + 1, (value & 0xFF) >> 8)
        self.writeByte(address + 1, value >> 8)

    def loadROM(self, romFileName):
        if not os.path.exists(romFileName):
            raise FileNotFoundError

        i = 0
        with open(romFileName, 'rb') as f:
            while True:
                buffer = f.read(4096)

                for d in range(len(buffer)):
                    self.ROM.writeByte(i, d)
                    i += 1

                if len(buffer) == 0:
                    self.cartType = self.ROM.readByte(0x147)
                    self.log.debug(
                        'ROM loaded, bytes %i, cartridge type %X' %
                        (i, self.cartType)
                    )
                    break
