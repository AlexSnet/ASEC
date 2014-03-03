class OutOfRangeException(Exception):
    pass


class MemoryBank:
    def __init__(self, size=0):
        self._size = int(size)
        self._buffer = {}
        self.reset()

    def reset(self):
        """
        reset memory
        """
        self._buffer = dict(((i, 0) for i in range(self.size)))

    def __len__(self):
        return self._size

    @property
    def size(self):
        """
        memory size
        @return int
        """
        return self._size


    def writeWord(self, address, value):
        """
        write 16 bit word
        @param address int
        @param value int
        """
        self.writeByte(address, value & 0xFF)
        self.writeByte(address + 1, (value & 0xFF) >> 8)

    def readWord(self, address):
        """
        read 16 bit word
        @param address int
        @return int
        """
        return self.readByte(address) + (self.readByte(address + 1) << 8)

    def writeByte(self, address, value):
        """
        write byte
        @param address int
        @param value int
        """
        if address < 0 or address >= self.size:
            raise OutOfRangeException('Out of range %x, (size %x)' % (address, self.size))

        self._buffer[address] = value

    def readByte(self, address):
        """
        read byte
        @param address int
        @return int
        """
        if address < 0 or address >= self.size:
            raise OutOfRangeException('Out of range %x, (size - %x)' % (address, self.size))

        return self._buffer[address]

    def __getitem__(self, item):
        return self.readByte(item)

    def __getattr__(self, item):
        return self.readByte(item)
