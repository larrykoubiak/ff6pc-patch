from struct import pack, unpack
import os

class ObbFile:
    def __init__(self, path, filelist):
        self.__files = {}
        self.__path = path
        self.__filelist = filelist
        self.signature = 0X01424258
        if path:
            self.__parseFile()
    
    def __parseFile(self):
        f = open(self.__path,"rb")
        sig = unpack("<I", f.read(4))[0]
        if sig != self.signature:
            print("Invalid Signature for OBB File")
        nbfiles = unpack("<I", f.read(4))[0]
        f.seek(24, 1)
        for _ in range(nbfiles):
            offset, size, _, hash = unpack("<IIII", f.read(16))
            if hash in self.__filelist:
                name = self.__filelist[hash]
                fileentry = ObbEntry(name, offset,size)
                self.__files[fileentry.Name] = fileentry
        f.close()

    def __decryptData(self, data):
        v = 0x60BDCB ##Magic number!
        ##Groups of 4 bytes at a time first
        size4 = int(len(data)/4)
        for i in range(size4):
            ##Magic numbers!
            t = v*0x12FCF0A
            v = (t + 0x0BA53A7) & 0xFFFFFFFF
            xor = unpack("<I",data[i*4:i*4 + 4])[0]
            newVal = (xor ^ v) & 0xFFFFFFFF
            ##Assign new value
            newValBytes = pack("<I",newVal)
            data[i*4 + 0] = newValBytes[0]
            data[i*4 + 1] = newValBytes[1]
            data[i*4 + 2] = newValBytes[2]
            data[i*4 + 3] = newValBytes[3]
        ##Remaining bytes, if not a multiple of 4
        if size4*4 != len(data):
            for i in range(size4*4, len(data)):
                t = v*0x12FCF0A
                v = t + 0x0BA53A7
                val = v >> 24
                data[i] = (data[i] ^ val) & 0xFF
        return data

    def ReadEntry(self, filename):
        if filename in self.__files:
            entry = self.__files[filename]
            f = open(self.__path,"rb")
            f.seek(entry.Offset)
            crypteddata = f.read(entry.Size)
            entry.Data = self.__decryptData(bytearray(crypteddata))

    @property
    def Files(self):
        return self.__files

class ObbEntry:
    def __init__(self, name, offset, size):
        self.__name = name
        self.__offset = offset
        self.__size = size
        self.__data = None

    def Export(self):
        path = 'output/' + self.__name
        os.makedirs(os.path.dirname(path),exist_ok=True)
        if self.__data:
            f = open(path, 'wb')
            f.write(self.__data)
            f.close()

    @property
    def Name(self):
        return self.__name

    @property
    def Offset(self):
        return self.__offset

    @property
    def Size(self):
        return self.__size

    @property
    def Data(self):
        return self.__data

    @Data.setter
    def Data(self, val):
        self.__data = val

    def __str__(self):
        fmt = "Name: {0} Offset: {1:08X} Size: {2}"
        return fmt.format(self.__name, self.__offset, self.__size)

    def __repr__(self):
        return str(self)