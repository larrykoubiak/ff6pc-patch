class Spritesheet:
    def __init__(self, data, palette, mode="4bpp"):
        self.__data = data
        self.__palette = palette
        self.__mode = mode
        self.__sprites = []
        if data is not None:
            self.__readPixels()

    @property
    def PaletteId(self):
        return self.__palette

    @property
    def Sprites(self):
        return self.__sprites

    def __readPixels(self):
        curofs = 0
        if self.__mode=="4bpp":
            nbsprites = len(self.__data) >> 5
            for _ in range(nbsprites):
                pixels = []
                for i in range(32):
                    pixels2 = self.__data[curofs+i]
                    pixels.append(pixels2 & 0xF)
                    pixels.append(pixels2 >> 4)
                curofs += 32
                self.__sprites.append(pixels)
        elif self.__mode=="8bpp":
            nbsprites = len(self.__data) >> 6
            for _ in range(nbsprites):
                pixels = self.__data[curofs:curofs+64]
                curofs += 64
                self.__sprites.append(pixels)