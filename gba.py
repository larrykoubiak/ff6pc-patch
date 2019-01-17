from PIL import Image
from struct import unpack

def open_rom(path):
    data = None
    if path:
        f = open(path, 'rb')
        data = f.read()
    return data

def open_palettes(data, offset, nb_palettes = 16, mode="bgr"):
    palettes = []
    palofs = offset
    for _ in range(nb_palettes):
        palette = []
        for colid in range(16):
            color = unpack("<H",data[palofs + (colid*2):palofs + (colid*2) + 2])[0]
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
        palettes.append(palette)
    return palettes

def open_sprites(data, offset, nb_sprites, mode="4bpp"):
    sprites = []
    curofs = offset
    for _ in range(nb_sprites):
        pixels = []
        if mode=="4bpp":
            for i in range(32):
                pixels2 = data[curofs+i]
                pixels.append(pixels2 & 0xF)
                pixels.append(pixels2 >> 4)
            curofs += 32
        elif mode=="8bpp":
            pixels = data[curofs:curofs+64]
            curofs += 64
        sprites.append(pixels)
    return sprites

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
    rom = open_rom('output/misc/rom.gba')
    pals = open_palettes(rom, 0x6FD8E6, 256, "bgr")
    sprites = open_sprites(rom, 0x760000,181)
    create_image(pals[2], sprites, 64, 184, "output/test.gif")

if __name__ == "__main__":
    main()