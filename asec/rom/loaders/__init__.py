from asec.memory.rom import ROM


class DefaultLoader(object):
    def __init__(self, cartridge):
        self.cartridge = cartridge
        self.ROM = ROM(self.rom_size)

    def read(self):
        raise NotImplementedError

    @property
    def name(self):
        return self._name if hasattr(self, '_name') else 'Unknown'

    @property
    def rom_size(self):
        return getattr(self, '_rom_size', 0x100000)

    def emulator(self):
        """
        @return Device
        """
        raise NotImplementedError
