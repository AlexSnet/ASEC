import os
import array


class OutOfRangeException(Exception):
    pass


class MemoryBank:
    def __init__(self, size=0):
        self._size = int(size)
        self._buffer = None
        self.reset()

    def reset(self, fill=True):
        """
        reset memory
        """
        del self._buffer
        self._buffer = array.array('B')

        if fill:
            for i in range(self.size):
                self._buffer.append(0x00)

        # self._buffer = dict(((i, 0) for i in range(self.size)))

    def load(self, f):
        f.seek(0, os.SEEK_END)
        size = f.tell()

        f.seek(0)
        self.reset(fill=False)
        self._buffer.fromfile(f, size)
        while self._buffer.buffer_info()[1] < self.size:
            self._buffer.append(0x00)

    def dump(self, fp):
        return fp.write(self.dumps())

    def dumps(self):
        return self._buffer.tostring()

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
        if (address < 0) or (address >= self.size):
            raise OutOfRangeException('Out of range %x, (size %x)' % (address, self.size))
        #print('writeByte', address, value)
        try:
            self._buffer.insert(address, value & 0xFF)
        except Exception as e:
            print(e)
            print(address, value)
        # self._buffer[address] = value

    def readByte(self, address):
        """
        read byte
        @param address int
        @return int
        """
        if (address < 0) or (address >= self.size):
            raise OutOfRangeException('Out of range %x, (size - %x)' % (address, self.size))

        return self._buffer[address]

    def __getitem__(self, item):
        return self.readByte(item)

    def __getattr__(self, item):
        return self.readByte(item)

    def __setitem__(self, key, value):
        self.writeByte(key, value)
