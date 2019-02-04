from PIL import Image
from rom import gbarom

def draw_sprite(imagedata, width, col,row,sprite=None,hflip=False,vflip=False):
    for yoffset in range(8):
        for xoffset in range(8):
            y = (row*8) + (7-yoffset) if vflip else (row*8) + yoffset
            x = (col * 8) + (7-xoffset) if hflip else (col * 8) + xoffset
            destoffset = (y * width) + x
            if sprite is None:
                imagedata[destoffset] = 0
            else:
                imagedata[destoffset] = sprite[(yoffset*8)+xoffset]

def create_image(palette,sprites,layouts,width,height, path):
    imagedata = bytearray(width*height)
    numcols = int(width/16)
    for layoutidx in range(40):
        layout = layouts[layoutidx]
        row = int((layoutidx) / numcols) * 3
        col = ((layoutidx) % numcols) * 2
        for spridx in range(6):
            spriteid = layout[spridx]
            destrow = row + int(spridx / 2)
            destcol = col + (spridx % 2)
            if spriteid == 0xFFFF or spriteid >= (len(sprites)*32):
                sprite = None
            else:
                sprite = sprites[(spriteid>>5)]
            draw_sprite(imagedata,width,destcol,destrow,sprite)
    image = Image.frombytes("P", (width, height), bytes(imagedata))
    image.putpalette(palette)
    image.save(path)

def main():
    rom = gbarom('output/misc/rom.gba')
    for idx in range(24):
        ss = rom.SpriteSheets[idx]
        create_image(rom.Palettes[ss.PaletteId], ss.Sprites, rom.SpriteLayouts, 160, 96, "output/test_" +str(idx) + ".gif")

if __name__ == "__main__":
    main()