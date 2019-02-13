from struct import unpack
from spritesheet import Spritesheet
from json import load

class gbarom:
    def __init__(self, data =None):
        with open("data/rommap.json","r") as f: 
            self.__rommap = load(f)
        self.__data = data
        self.__palettes = {}
        self.__spritedata = {}
        self.__spritelayouts = {}
        self.__spritesheets = {}
        if data is not None:
            self.__parseBytes(data)

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


    def __parseBytes(self, data):
        for table_name, v in self.__rommap.items():
            self.__readPaletteData(
                table_name, 
                v["palette"])
            self.__readSpriteDataFromOffsets(
                table_name,
                v["spritedata"])
            self.__readSpriteLayouts(
                table_name,
                v["spritelayout"],
                None if "layout_translate" not in v else v["layout_translate"])
            self.__readSpriteSheetData(
                table_name, 
                v["spritesheet"])
        ## Portraits
        # self.__readPaletteData(0x5FE55E,"character_portraits",23, "bgr")
        # self.__readSpritesheetBySpriteCount(0x5FE83E,"character_portraits",25,23)
        # self.__spritelayouts["character_portraits"] = [(0,1,2,3)]

    def __read24(self, start, offset,bankoffset=2):
        offs = unpack("<H",self.__data[start + offset:start + offset + 2])[0]
        bank = self.__data[start + offset + bankoffset]
        return (bank << 16) + offs
    
    def __read1555(self, start, offset):
        val = unpack("<H",self.__data[start + offset:start + offset + 2])[0]
        result = ((val & 0x8000) >> 15, (val & 0x7C00) >> 10, (val & 0x03E0) >> 5, val & 0x001F)
        return result

    def __readPaletteData(self, table_name, params):
        self.__palettes[table_name] = []
        palofs = params["offset"]
        mode = params["format"]
        for _ in range(params["length"]):
            palette = []
            for colid in range(16):
                if mode=="bgr":
                    _, b, g, r = self.__read1555(palofs, colid * 2)
                elif mode=="rgb":
                    _, r, g, b = self.__read1555(palofs, colid * 2)
                else:
                    r = g = b = 0
                palette.extend(((r << 3) + 4, (g  << 3) + 4,(b << 3) + 4))
            palofs += 32
            self.__palettes[table_name].append(palette)

    def __readSpritesheetBySpriteCount(self, offset, table_name, nb_sprites, nb_sheets, mode="4bpp"):
        self.__spritedata[table_name] = {}
        self.__spritesheets[table_name] = []
        sheetofs = offset
        for idx in range(nb_sheets):
            startoffset = sheetofs + (idx * nb_sprites * 32)
            endoffset = startoffset + (nb_sprites * 32)
            self.__spritedata[table_name][idx] = self.__data[startoffset:endoffset]
            ss = Spritesheet(self.__data[startoffset:endoffset], idx)
            self.__spritesheets[table_name].append(ss)

    def __readSpriteDataFromOffsets(self,  table_name, params):
        self.__spritedata[table_name] = {}
        offset = params["offset"]
        for idx in range(params["length"]):
            spritesheetkey = self.__read24(offset,(idx * 2), 0x14A)
            startoffset = spritesheetkey & 0x7FFFFF 
            if idx == (params["length"]-1):
                endoffset = (startoffset + 256)
            else:
                endoffset = self.__read24(offset,(idx * 2) + 2, 0x14A) & 0x7FFFFF
            self.__spritedata[table_name][spritesheetkey] = self.__data[startoffset:endoffset]

    def __readSpriteLayouts(self, table_name, params, translate_table=None):
        layouts = []
        sheetofs = params["offset"]
        for idx in range(params["length"]):
            offsets = unpack("<HHHHHH", self.__data[sheetofs+(idx*12):sheetofs+(idx*12)+12])
            layouts.append(offsets)
        if "exceptions" in params:
            for exception in params["exceptions"]:
                layouts[exception["id"]] = tuple(exception["value"])
        if translate_table is not None:
            newlayouts = []
            for idx in range(len(translate_table)):
                newlayouts.append(layouts[translate_table[idx]])
            self.__spritelayouts[table_name] = newlayouts
        else:
            self.__spritelayouts[table_name] = layouts

    def __readSpriteSheetData(self, table_name, params):
        self.__spritesheets[table_name] = []
        for idx in range(params["length"]):
            palidx = self.__data[params["palid_offset"] + idx]
            key = self.__read24(params["sprid_offset"],idx * 3)
            ss = Spritesheet(self.__spritedata[table_name][key], palidx, params["mode"])
            self.__spritesheets[table_name].append(ss)
        if "exceptions" in params:
            for exception in params["exceptions"]:
                if exception["field"] == "palidx":
                    self.__spritesheets[table_name][exception["id"]].PaletteId = exception["value"]

if __name__ == "__main__":
    data = open("output/misc/rom.bin", "rb").read() 
    rom = gbarom(data)
    for sl in rom.SpriteLayouts["character_sprites"]:
        print(" ".join('%04X' % s for s in sl))