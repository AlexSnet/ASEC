from asec.rom.loaders import DefaultLoader


CARTRIDGE_TYPES_REPR = {
    0x00: "ROM ONLY",		        0x13: "MBC3+RAM+BATTERY",
    0x01: "MBC1",			        0x15: "MBC4",
    0x02: "MBC1+RAM",		        0x16: "MBC4+RAM",
    0x03: "MBC1+RAM+BATTERY",   	0x17: "MBC4+RAM+BATTERY",
    0x05: "MBC2",		        	0x19: "MBC5",
    0x06: "MBC2+BATTERY",	    	0x1A: "MBC5+RAM",
    0x08: "ROM+RAM",		        0x1B: "MBC5+RAM+BATTERY",
    0x09: "ROM+RAM+BATTERY",    	0x1C: "MBC5+RUMBLE",
    0x0B: "MMM01",		        	0x1D: "MBC5+RUMBLE+RAM",
    0x0C: "MMM01+RAM",		        0x1E: "MBC5+RUMBLE+RAM+BATTERY",
    0x0D: "MMM01+RAM+BATTERY",	    0x22: "MBC7+BATTERY",
    0x0F: "MBC3+TIMER+BATTERY",	    0xFC: "POCKET CAMERA",
    0x10: "MBC3+TIMER+RAM+BATTERY",	0xFD: "BANDAI TAMA5",
    0x11: "MBC3",			        0xFE: "HuC3",
    0x12: "MBC3+RAM",		        0xFF: "HuC1+RAM+BATTERY"
}


class InfoLoader(DefaultLoader):
    def __init__(self, cartridge):
        self._rom_size = 0x100000
        super(InfoLoader, self).__init__(cartridge)

    def read(self):
        self.ROM.load(self.cartridge._fd)
        # for i, b in enumerate(self.cartridge._fd.read()):
        #     self.ROM[i] = b  # ord(b)

        # 0134 - 0143 - Title
        title = ""
        for i in range(11):
            s = self.ROM[i + 0x134]
            if s != 0:
                title = "%s%s" % (title, chr(s))
        if title:
            self._name = title
        print('Title:', title)

        # 0147 - Cartridge Type
        cartridge_type = self.ROM[0x147]
        self._cartridge_type = cartridge_type
        print('Cartridge type:', CARTRIDGE_TYPES_REPR[cartridge_type])

        # 0148 - ROM Size
        # Specifies the ROM Size of the cartridge.
        # Typically calculated as "32KB shl N".
        rom_size = self.ROM[0x148]
        self._rom_size = rom_size
        print('ROM size:', rom_size)

        # 0149 - RAM Size
        # Specifies the size of the external RAM in the cartridge (if any).
        ram_size = self.ROM[0x149]
        print('RAM Size:', ram_size)

        # 014A - Destination Code
        # Specifies if this version of the game is supposed
        #  to be sold in japan, or anywhere else.
        # Only two values are defined.
        destination_code = self.ROM[0x14A]  # 0x00 - Japan, 0x01 - Non-Japan
        print('Destination:', 'Japan' if destination_code == 0x00 else 'Non Japan')

        # 014B - Old Licensee Code
        # Specifies the games company/publisher code in range 00-FFh.
        # A value of 33h signalizes that the New License Code in
        #   header bytes 0144-0145 is used instead.
        # (Super GameBoy functions won't work if <> $33.)
        old_licensee_code = self.ROM[0x14B]
        print('License code:', old_licensee_code)

        # 014C - Mask ROM Version number
        # Specifies the version number of the game. That is usually 00h.
        mask_rom_version = self.ROM[0x14C]
        print('Mask ROM Version:', mask_rom_version)

        # 014D - Header Checksum
        # Contains an 8 bit checksum across the
        #  cartridge header bytes 0134-014C.
        # The checksum is calculated as follows:
        header_checksum = self.ROM[0x14D]
        print('Header checksum:', header_checksum)

        # 014E-014F - Global Checksum
        # Contains a 16 bit checksum (upper byte first) across the whole cartridge ROM.
        # Produced by adding all bytes of the cartridge (except for the two checksum bytes).
        # The Gameboy doesn't verify this checksum.
        global_checksum = ((self.ROM[0x14E] << 8) & self.ROM[0x14D])
        print('Global checksum:', global_checksum)

    @property
    def type(self):
        return self._cartridge_type

    @property
    def type_string(self):
        return CARTRIDGE_TYPES_REPR[self.type]

    @property
    def rom_size(self):
        return self._rom_size

    @property
    def rom_size_string(self):
        return self._rom_size

    def emulator(self):
        from asec.asset.gb import Device
        emu = Device()
        emu.MMU.ROM = self.ROM
        emu.MMU.cartType = self.ROM.readByte(0x147)
        return emu
