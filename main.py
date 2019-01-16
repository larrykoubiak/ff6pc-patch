from filelist import FileList
from obb import ObbFile


def main():
    filelist = FileList("data/main.list")
    obb = ObbFile("data/main.obb", filelist.Files)
    files = sorted(list(obb.Files.values()), key=lambda x: x.Offset)
    for fe in files:
        print("Reading " + fe.Name)
        obb.ReadEntry(fe.Name)
        fe.Export()

if __name__ == "__main__":
    main()