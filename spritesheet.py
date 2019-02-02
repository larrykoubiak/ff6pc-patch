class spritesheet:
    def __init__(self, offset, length, data, mode="4bpp"):
        self.__length = length
        self.__sprites = []
        self.__mode = mode
        if offset is not None:
            self.__readPixels(data, offset)

    @property
    def Sprites(self):
        return self.__sprites

    def __readPixels(self, data, offset):
        curofs = offset
        if self.__mode=="4bpp":
            nbsprites = self.__length >> 5
            for _ in range(nbsprites):
                pixels = []
                for i in range(32):
                    pixels2 = data[curofs+i]
                    pixels.append(pixels2 & 0xF)
                    pixels.append(pixels2 >> 4)
                curofs += 32
                self.__sprites.append(pixels)
        elif self.__mode=="8bpp":
            nbsprites = self.__length >> 6
            for _ in range(nbsprites):
                pixels = data[curofs:curofs+64]
                curofs += 64
                self.__sprites.append(pixels)