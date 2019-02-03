from struct import unpack
from spritesheet import Spritesheet

class gbarom:
    def __init__(self, path=None):
        self.__data = None
        self.__palettes = []
        self.__spritedata = {}
        self.__spritelayouts = []
        self.__spritesheets = []
        if path is not None:
            self.__parseFile(path)

    @property
    def Palettes(self):
        return self.__palettes

    @property
    def SpriteData(self):
        return self.__spritedata

    @property
    def SpriteLayouts(self):
        return self.__spritelayouts

    @property
    def SpriteSheets(self):
        return self.__spritesheets


    def __parseFile(self, path):
        with open(path, 'rb') as f:
            self.__data = f.read()
            self.__readSpriteData(0x10C18,24)
            self.__readPaletteData(0x6FD8E6, 256, "bgr")
            self.__readSpriteLayouts(0xBB9AC,32)
            self.__readSpriteSheetData()

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

    def __readSpriteData(self, offset, nb_sheets, mode="4bpp"):
        sheetofs = offset
        bankofs = offset + 0x14C
        for idx in range(nb_sheets):
            startbank = unpack("<H",self.__data[bankofs+(idx*2):bankofs+(idx*2)+2])[0]
            startsproffs = unpack("<H",self.__data[sheetofs+(idx*2):sheetofs+(idx*2)+2])[0]
            startoffset = ((startbank & 0x7F)<<16) + startsproffs
            spritesheetkey = ((startbank & 0xFF) << 16) + startsproffs
            endbank = unpack("<H",self.__data[bankofs+(idx*2)+2:bankofs+(idx*2)+4])[0]
            endsproffs = unpack("<H",self.__data[sheetofs+(idx*2)+2:sheetofs+(idx*2)+4])[0]
            endoffset = ((endbank & 0x7F)<<16) + endsproffs
            if endoffset == 0:
                endoffset = startoffset + 256
            self.__spritedata[spritesheetkey] = self.__data[startoffset:endoffset]

    def __readSpriteLayouts(self, offset, nb_layouts):
        sheetofs = offset
        for idx in range(nb_layouts):
            offsets = unpack("<HHHHHHHH", self.__data[sheetofs+(idx*16):sheetofs+(idx*16)+16])
            self.__spritelayouts.append(offsets)

    def __readSpriteSheetData(self):
        palidxoffs = 0XBC092
        spridxoffs = 0xBC0AA
        for idx in range(24):
            palidx = self.__data[palidxoffs + idx]
            offs = unpack("<H",self.__data[spridxoffs+(idx*3):spridxoffs+(idx*3)+2])[0]
            bank = self.__data[spridxoffs+(idx*3)+2]
            key = (bank << 16) + offs
            ss = Spritesheet(self.__spritedata[key], palidx,"4bpp")
            self.__spritesheets.append(ss)

if __name__ == "__main__":
    rom = gbarom('output/misc/rom.gba')
    for sl in rom.SpriteLayouts:
        print(" ".join('%04X' % s for s in sl))