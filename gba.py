from PIL import Image
from struct import unpack
from rom import gbarom

def create_image(palette,sprites,width,height, path):
    cols = int(width / 8)
    rows = int(height / 8)
    imagedata = bytearray(width*height)
    offset = 0
    for r in range(rows):
        for y in range(8):
            for c in range(cols):
                spriteid = (r * cols) + c
                if spriteid >= len(sprites):
                    for _ in range(8):
                        imagedata[offset] = 0
                        offset +=1
                else:
                    sprite = sprites[spriteid]
                    for x in range(8):
                        imagedata[offset] = sprite[(y*8)+x]
                        offset += 1
    image = Image.frombytes("P", (width, height), bytes(imagedata))
    image.putpalette(palette)
    image.save(path)

def main():
    rom = gbarom('output/misc/rom.gba')
    for idx in range(24):
        palidx = rom.PaletteIndexes[idx]
        create_image(rom.Palettes[palidx], rom.SpriteData[idx].Sprites, 64, 184, "output/test_" +str(idx) + ".gif")

if __name__ == "__main__":
    main()