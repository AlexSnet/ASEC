from asec.memory.rom import ROM


class DefaultLoader:
    def __init__(self, cartridge):
        self.cartridge = cartridge
        self.ROM = ROM(self._rom_size)

    def read(self):
        raise NotImplementedError

    @property
    def name(self):
        return self._name if hasattr(self, '_name') else 'Unknown'

    def emulator(self):
        """
        @return Device
        """
        raise NotImplementedError