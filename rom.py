from struct import unpack
from spritesheet import spritesheet

class gbarom:
    def __init__(self, path=None):
        self.__data = None
        self.__palettes = []
        self.__paletteindexes = []
        self.__spritedata = []
        if path is not None:
            self.__parseFile(path)

    @property
    def Palettes(self):
        return self.__palettes

    @property
    def PaletteIndexes(self):
        return self.__paletteindexes

    @property
    def SpriteData(self):
        return self.__spritedata

    def __parseFile(self, path):
        with open(path, 'rb') as f:
            self.__data = f.read()
            self.__readPaletteData(0x6FD8E6, 256, "bgr")
            self.__readPaletteIndexes(0XBC092,24)
            self.__readSpriteData(0x10C18,24)

    def __readPaletteData(self, offset, nb_palettes = 16, mode="bgr"):
        palofs = offset
        for _ in range(nb_palettes):
            palette = []
            for colid in range(16):
                color = unpack("<H",self.__data[palofs + (colid*2):palofs + (colid*2) + 2])[0]
                if mode=="bgr":
                    b = color >> 10
                    g = (color & 0x3FF) >> 5
                    r = color & 0x1F
                elif mode=="rgb":
                    r = color >> 10
                    g = (color & 0x3FF) >> 5
                    b = color & 0x1F
                else:
                    r = g = b = 0
                palette.extend(((r << 3) + 4, (g  << 3) + 4,(b << 3) + 4))
            palofs += 32
            self.__palettes.append(palette)

    def __readPaletteIndexes(self, offset, nb_indexes):
        palidxoffs = offset
        for idx in range(nb_indexes):
            palidx = self.__data[palidxoffs + idx]
            self.__paletteindexes.append(palidx)

    def __readSpriteData(self, offset, nb_sheets, mode="4bpp"):
        sheetofs = offset
        bankofs = offset + 0x14C
        for idx in range(nb_sheets):
            startbank = unpack("<H",self.__data[bankofs+(idx*2):bankofs+(idx*2)+2])[0]
            startsproffs = unpack("<H",self.__data[sheetofs+(idx*2):sheetofs+(idx*2)+2])[0]
            startoffset = ((startbank & 0x7F)<<16) + startsproffs
            endbank = unpack("<H",self.__data[bankofs+(idx*2)+2:bankofs+(idx*2)+4])[0]
            endsproffs = unpack("<H",self.__data[sheetofs+(idx*2)+2:sheetofs+(idx*2)+4])[0]
            endoffset = ((endbank & 0x7F)<<16) + endsproffs
            if endoffset == 0:
                endoffset = startoffset + 256
            length = (endoffset-startoffset)
            ss = spritesheet(startoffset, length, self.__data, mode)
            self.__spritedata.append(ss)


if __name__ == "__main__":
    rom = gbarom('output/misc/rom.gba')
    for ss in rom.SpriteData:
        print(ss.Sprites)