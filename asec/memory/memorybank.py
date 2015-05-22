import os
import array
import logging

from asec.utils.hexdump import hexdump


class OutOfRangeException(Exception):
    pass


class MemoryBank(object):
    def __init__(self, size=0):
        self.log = logging.getLogger(self.__class__.__name__)

        self._size = int(size)
        self._buffer = None

        self.reset()

    def reset(self, fill=True):
        """
        reset memory
        """
        def initializer():
            for i in range(self.size):
                yield 0x00

        del self._buffer
        self._buffer = array.array('B', initializer())

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
        self.log.debug('writeWord 0x%06X at 0x%06X', value, address)

        self.writeByte(address, value & 0xFF)
        self.writeByte(address + 1, (value & 0xFF) >> 8)

    def readWord(self, address):
        """
        read 16 bit word
        @param address int
        @return int
        """
        self.log.debug('readWord at 0x%06X', address)
        return self.readByte(address) + (self.readByte(address + 1) << 8)

    def writeByte(self, address, value):
        """
        write byte
        @param address int
        @param value int
        """
        self.log.debug('writeByte 0x%06X at 0x%06X', value, address)

        if (address < 0) or (address >= self.size):
            raise OutOfRangeException(
                'Out of range 0x%06X, (size 0x%06X)' %
                (address, self.size)
            )

        try:
            self._buffer.insert(address, value & 0xFF)
        except Exception as e:
            self.log.error('can not write byte to 0x%06X', address)
            print(hexdump(self.dumps()))
            raise e
            # print(address, value)
        # self._buffer[address] = value

    def readByte(self, address):
        """
        read byte
        @param address int
        @return int
        """
        self.log.debug('readByte at 0x%06X', address)

        if (address < 0) or (address >= self.size):
            raise OutOfRangeException(
                'Out of range 0x%06X, (size 0x%06X)' %
                (address, self.size)
            )

        try:
            return self._buffer[address]
        except Exception as e:
            self.log.error('can not read byte at 0x%06X', address)
            print(hexdump(self.dumps()))
            raise e

    def __getitem__(self, item):
        return self.readByte(item)

    def __getattr__(self, item):
        return self.readByte(item)

    def __setitem__(self, key, value):
        self.writeByte(key, value)
