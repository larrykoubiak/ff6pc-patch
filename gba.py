from PIL import Image
from rom import gbarom
import os

class GBA:
    def __init__(self, rom):
        self.__rom = gbarom(rom)

    def __create_image(self, palette,spritesheet, path):
        ss = spritesheet
        image = Image.frombytes("P", (ss.Width, ss.Height), bytes(ss.ImageData))
        image = image.resize((512,256), Image.NEAREST)
        image.putpalette(palette)
        if os.path.exists(path):
            os.remove(path)
        os.makedirs(os.path.dirname(path),exist_ok=True)
        image.save(path)

    def __translate_NPClayouts(self, origlayouts):
        NPClayouts=[]
        translateNPC = (
            0,1,2,3,4,5,6,7,8,42,43,44,41
        )
        for idx in range(13):
            NPClayouts.append(origlayouts[translateNPC[idx]])
        return NPClayouts

    def extract_character_sprites(self):
        PCs = list(range(22))
        for idx in PCs:
            ss = self.__rom.SpriteSheets["character_sprites"][idx]
            palette = self.__rom.Palettes["character_sprites"][ss.PaletteId]
            self.__create_image(
                palette,
                ss,
                "output/character/char" + '%02x' % idx + ".bmp")

if __name__ == "__main__":
    rom = open("output/misc/rom.bin", "rb").read()
    gba = GBA(rom)
    gba.extract_character_sprites()