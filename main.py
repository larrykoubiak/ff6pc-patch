from filelist import FileList
from obb import ObbFile
from gba import GBA

def main():
    filelist = FileList("data/main.list")
    obb = ObbFile("data/main.obb", filelist.Files)
    fe = obb.Files["misc/rom.bin.gz"]
    obb.ReadEntry(fe.Name)
    gba = GBA(fe.Data)
    gba.extract_character_sprites()

if __name__ == "__main__":
    main()