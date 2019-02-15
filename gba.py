from PIL import Image
from rom import gbarom
import os

class GBA:
    def __init__(self, rom):
        self.__rom = gbarom(rom)

    def __create_image(self, palette,spritesheet, path):
        ss = spritesheet
        image = Image.frombytes("P", (ss.Width, ss.Height), bytes(ss.ImageData))
        image = image.resize((ss.Width * 2, ss.Height * 2), Image.NEAREST)
        image.putpalette(palette)
        if os.path.exists(path):
            os.remove(path)
        os.makedirs(os.path.dirname(path),exist_ok=True)
        image.save(path)

    def extract_sprites(self):
        for table_name, v in self.__rom.SpriteSheets.items():
            for idx in range(len(v)):
                ss = self.__rom.SpriteSheets[table_name][idx]
                palette = self.__rom.Palettes[table_name][ss.PaletteId]
                self.__create_image(
                    palette,
                    ss,
                    "output/" + table_name + "/char" + '%02x' % idx + ".bmp")

if __name__ == "__main__":
    rom = open("output/misc/rom.bin", "rb").read()
    gba = GBA(rom)
    gba.extract_sprites()