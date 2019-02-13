class Spritesheet:
    def __init__(self, data, paletteid, layouts=None, mode="4bpp"):
        self.__data = data
        self.__paletteid = paletteid
        self.__mode = mode
        self.__sprites = []
        self.__layouts = layouts
        self.__frames = []
        self.__imagedata = bytearray()
        if data is not None:
            self.__readSprites()

    @property
    def PaletteId(self):
        return self.__paletteid

    @PaletteId.setter
    def PaletteId(self, value):
        self.__paletteid = value

    @property
    def Sprites(self):
        return self.__sprites

    def __readSprites(self):
        curofs = 0
        nbsprites = len(self.__data) >> (5 if self.__mode=="4bpp" else 6)
        spritelen = 32 if self.__mode=="4bpp" else 64
        for _ in range(nbsprites):
            sprite = Sprite(self.__data[curofs:curofs+spritelen], self.__mode)
            curofs += spritelen
            self.__sprites.append(sprite)

    def MakeFrames(self, layouts, palette, map):
        for layout in layouts:
            framesprites = [self.__sprites[s] for s in layout]
            f = Frame(framesprites, map)
            self.__frames.append(f)


class Frame:
    def __init__(self, sprites, map):
        self.__map = map
        self.__sprites = sprites
        self.__imagedata = None
        if map is not None:
            self.__width = len(map[0]) * 8
            self.__height = len(map) * 8
            self.__imagedata = bytearray(self.__width * self.__height)

    def Draw(self):
        for rowidx in range(len(self.__map)):
            row = self.__map(rowidx)
            for colidx in row:
                spriteid, hflip, vflip = row(colidx)
                sprite = self.__sprites[spriteid]
                sprite.Draw(self.__imagedata, self.__width, colidx * 8, rowidx * 8, hflip, vflip)

    @property
    def Width(self):
        return self.__width

    @property
    def Height(self):
        return self.__height

    @property
    def ImageData(self):
        return self.__imagedata


class Sprite:
    def __init__(self, data=None, mode="4bpp"):
        self.__pixels = []
        self.__mode = mode
        if data is not None:
            self.__readPixels(data)

    def __readPixels(self, data):
        if self.__mode=="4bpp":
            for i in range(32):
                pixels2 = data[i]
                self.__pixels.append(pixels2 & 0xF)
                self.__pixels.append(pixels2 >> 4)
        elif self.__mode=="8bpp":
            self.__pixels = data

    def Draw(self, targetimage, targetwidth, targetx, targety, hflip, vflip):
        for yoffset in range(8):
            for xoffset in range(8):
                y = targety + ((7-yoffset) if vflip else yoffset)
                x = targetx + ((7-xoffset) if hflip else xoffset)
                destoffset = (y * targetwidth) + x
                targetimage[destoffset] = self.__pixels[(yoffset*8)+xoffset]

    @property
    def Pixels(self):
        return self.__pixels