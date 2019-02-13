from PIL import Image
from rom import gbarom
import os

class GBA:
    def __init__(self, rom):
        self.__rom = gbarom(rom)

    def __draw_sprite(self, imagedata, width, col,row,sprite=None,layout="V",hflip=False,vflip=False):
        rowoffset = 8 if layout=="H" else 0
        coloffset = 4 if layout=="V" else 0
        for yoffset in range(8):
            for xoffset in range(8):
                y = (row*8) + ((7-yoffset) if vflip else yoffset) + rowoffset
                x = (col * 8) + ((7-xoffset) if hflip else xoffset) + coloffset
                destoffset = (y * width) + x
                if sprite is None:
                    imagedata[destoffset] = 0
                else:
                    imagedata[destoffset] = sprite.Pixels[(yoffset*8)+xoffset]

    def __create_image(self, palette,sprites,layouts,width,height, path):
        imagedata = bytearray(width*height)
        numcols = int(width/24)
        spritecount = 0
        for layoutidx in range(len(layouts)):
            hFlip = False
            vFlip = False
            layout = layouts[layoutidx]
            row = int((spritecount) / numcols) * 3
            col = ((spritecount) % numcols) * 3
            for spridx in range(6):
                if layoutidx in (2, 5):
                    newidx = 5 if spridx == 4 else 4 if spridx == 5 else spridx
                    spriteid = layout[newidx]
                    hFlip = True if spridx in (4,5) else False
                else:
                    spriteid = layout[spridx]
                    hFlip = False
                destrow = row + int(spridx / (3 if layoutidx == 23 else 2))
                destcol = col + (spridx % (3 if layoutidx == 23 else 2))
                if spriteid == 0xFFFF or spriteid >= (len(sprites)*32):
                    sprite = None
                else:
                    sprite = sprites[(spriteid>>5)]
                spritelayout = "H" if layoutidx==23 else "V"
                self.__draw_sprite(
                    imagedata,width,destcol,destrow,
                    sprite,spritelayout,hFlip,vFlip)
            spritecount += 1
        image = Image.frombytes("P", (width, height), bytes(imagedata))
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
        # PClayouts = self.__translate_PClayouts(self.__rom.SpriteLayouts["character_sprites"])
        PCs = list(range(22))
        for idx in PCs:
            ss = self.__rom.SpriteSheets["character_sprites"][idx]
            palette = self.__rom.Palettes["character_sprites"][ss.PaletteId]
            self.__create_image(
                palette,
                ss.Sprites,
                self.__rom.SpriteLayouts["character_sprites"], 
                256,
                128,
                "output/character/char" + '%02x' % idx + ".bmp")
        # NPClayouts = self.__translate_NPClayouts(self.__rom.SpriteLayouts["character_sprites"])
        # ss = self.__rom.SpriteSheets["character_sprites"][22]
        # palette = self.__rom.Palettes["character_sprites"][ss.PaletteId]
        # palette[0:3] = [0, 100, 0]
        # self.__create_image(palette, ss.Sprites, NPClayouts, 256, 128, "output/character/char16.bmp")

if __name__ == "__main__":
    rom = open("output/misc/rom.bin", "rb").read()
    gba = GBA(rom)
    gba.extract_character_sprites()