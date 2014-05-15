from asec.graphics.pixel import Pixel


class Screen:
    def __init__(self, pixel_w, pixel_h):
        self._width = pixel_w
        self._height = pixel_h

        self._pixels = {}
        self.reset()

    def reset(self):
        for i in range(self.width * self.height):
            self._pixels[i] = Pixel(255, 255, 255)

    @property
    def pixels(self):
        return self._pixels

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def toImage(self):
        from PIL import Image
        img = Image.new('RGB', (self.width, self.height))
        for x in range(self.width):
            for y in range(self.height):
                img.putpixel((x, y), self._pixels[x+(self.width*y)].hex)
        return img

    def toDataArray(self):
        data = []
        for x in range(self.width):
            for y in range(self.height):
                data.append(self._pixels[x+(self.width*y)].red)
                data.append(self._pixels[x+(self.width*y)].green)
                data.append(self._pixels[x+(self.width*y)].blue)
        return data

