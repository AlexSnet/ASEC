import os
import logging
from gzip import GzipFile


class Loader:
    def __init__(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError

        self.log = logging.getLogger('Loader')

        self.path = path
        self._fd = None

        ext = os.path.basename(self.path).split('.')[-1]
        if ext in ['gb', 'gbc', 'gba', 'gbz']:
            from asec.rom.loaders.gb import InfoLoader
            self.loader = InfoLoader(self)
        elif ext in ['sms', 'smc', 'smz']:
            from asec.rom.loaders.sega import InfoLoader
            self.loader = InfoLoader(self)

    def read(self):
        try:
            if self.path[-1] == 'z':
                try:
                    fd = GzipFile(self.path)
                except:
                    fd = open(self.path, 'rb')
                self._fd = fd
            else:
                self._fd = open(self.path, 'rb')
        except Exception as e:
            self.log.error('Can not load ROM', e)
        else:
            self.loader.read()

    def __del__(self):
        if self._fd:
            self._fd.close()

    @property
    def name(self):
        return self.loader.name

