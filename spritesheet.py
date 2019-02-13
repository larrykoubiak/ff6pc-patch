class Spritesheet:
    def __init__(self, data, paletteid, width, height, layouts=None, mode="4bpp"):
        self.__data = data
        self.__paletteid = paletteid
        self.__mode = mode
        self.__sprites = []
        self.__layouts = layouts
        self.__frames = []
        self.__width = width
        self.__height = height
        self.__imagedata = bytearray(width * height)
        if data is not None:
            self.__readSprites()
        if layouts is not None:
            self.__readLayouts()

    @property
    def PaletteId(self):
        return self.__paletteid

    @PaletteId.setter
    def PaletteId(self, value):
        self.__paletteid = value

    @property
    def Width(self):
        return self.__width

    @property
    def Height(self):
        return self.__height

    @property
    def ImageData(self):
        return self.__imagedata



    def __readSprites(self):
        curofs = 0
        nbsprites = len(self.__data) >> (5 if self.__mode=="4bpp" else 6)
        spritelen = 32 if self.__mode=="4bpp" else 64
        for _ in range(nbsprites):
            sprite = Sprite(self.__data[curofs:curofs+spritelen], self.__mode)
            curofs += spritelen
            self.__sprites.append(sprite)

    def __readLayouts(self):
        for layout in self.__layouts:
            framesprites = [self.__sprites[s >> 5] for s in layout.Offsets if (s >> 5) < len(self.__sprites)]
            if len(framesprites)==len(layout.Offsets):
                f = Frame(framesprites, layout.FrameMap)
                self.__frames.append(f)
        self.__draw()

    def __draw(self):
        framecount = 0
        numcols = int(self.__width/24)
        for frame in self.__frames:
            row = int((framecount) / numcols)
            col = ((framecount) % numcols)
            rowoffset = 8 if frame.Width > frame.Height else 0
            coloffset = 4 if frame.Width < frame.Height else 0
            for y in range(frame.Height):
                for x in range(frame.Width):
                    destx = (col * 24) + coloffset + x
                    desty = (row * 24) + rowoffset + y
                    srcoffset = (y * frame.Width) + x
                    destoffset = (desty * self.__width) + destx
                    self.__imagedata[destoffset] = frame.ImageData[srcoffset]
            framecount += 1

class Layout:
    def __init__(self, offsets=[], framemap=None):
        self.__offsets = offsets
        self.__framemap = None
        if framemap is not None:
            self.ReadFrameMap(framemap)

    def ReadFrameMap(self, framemap):
        self.__framemap = []
        for row in framemap:
            framerow = []
            for col in row:
                mapentry = MapEntry(col[0], col[1], col[2])
                framerow.append(mapentry)
            self.__framemap.append(framerow)

    @property
    def Offsets(self):
        return self.__offsets

    @Offsets.setter
    def Offsets(self, value):
        self.__offsets = value

    @property
    def FrameMap(self):
        return self.__framemap

    @FrameMap.setter
    def FrameMap(self, value):
        self.__framemap = value


class MapEntry:
    def __init__(self, spriteid, hflip=False, vflip=False):
        self.__spriteid = spriteid
        self.__hflip = hflip
        self.__vflip = vflip

    @property
    def SpriteId(self):
        return self.__spriteid

    @property
    def HFlip(self):
        return self.__hflip

    @property
    def VFlip(self):
        return self.__vflip

class Frame:
    def __init__(self, sprites, framemap):
        self.__sprites = sprites
        self.__framemap = framemap
        self.__imagedata = None
        if framemap is not None:
            self.__width = len(self.__framemap[0]) * 8
            self.__height = len(self.__framemap) * 8
            self.__imagedata = bytearray(self.__width * self.__height)
            self.__draw()

    def __draw(self):
        for rowidx in range(len(self.__framemap)):
            framerow = self.__framemap[rowidx]
            for colidx in range(len(framerow)):
                mapentry = framerow[colidx]
                sprite = self.__sprites[mapentry.SpriteId]
                x = colidx * 8
                y = rowidx * 8
                sprite.Draw(self.__imagedata, self.__width, x, y, mapentry.HFlip, mapentry.VFlip)

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