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
                    imagedata[destoffset] = sprite[(yoffset*8)+xoffset]

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

    def __translate_PClayouts(self, origlayouts):
        PClayouts=[]
        translatePC = (
            0,1,2,3,4,5,6,7,8,9,
            10,11,12,13,14,15,16,17,29,25,
            27,19,20,38,22,23,24,31,30,26,
            28,32,33,34,35,21,36,37,18,39,
            46,47)
        for idx in range(42):
            PClayouts.append(origlayouts[translatePC[idx]])
        ## add horizontal dead sprite
        PClayouts[23] = (0x0AE0, 0x0B00, 0xB20, 0x0B40, 0x0B60, 0x0B80)
        return PClayouts

    def __translate_NPClayouts(self, origlayouts):
        NPClayouts=[]
        translateNPC = (
            0,1,2,3,4,5,6,7,8,42,43,44,41
        )
        for idx in range(13):
            NPClayouts.append(origlayouts[translateNPC[idx]])
        return NPClayouts

    def extract_sprites(self):
        PClayouts = self.__translate_PClayouts(self.__rom.SpriteLayouts)
        PCs = list(range(22))
        for idx in PCs:
            ss = self.__rom.SpriteSheets[idx]
            palette = self.__rom.Palettes[8 if idx== 18 else ss.PaletteId]
            # palette[0:3] = [0, 100, 0]
            self.__create_image(palette, ss.Sprites, PClayouts, 256, 128, "output/character/char" + '%02x' % idx + ".bmp")
        NPClayouts = self.__translate_NPClayouts(self.__rom.SpriteLayouts)
        ss = self.__rom.SpriteSheets[22]
        palette = self.__rom.Palettes[ss.PaletteId]
        palette[0:3] = [0, 100, 0]
        self.__create_image(palette, ss.Sprites, NPClayouts, 256, 128, "output/character/char16.bmp")

if __name__ == "__main__":
    rom = open("output/misc/rom.bin", "rb").read()
    gba = GBA(rom)
    gba.extract_sprites()