class FileList:
    def __init__(self, path):
        self.__filelist = {}
        self.__path = path
        if path:
            self.__readfilelist()

    def __hashstring(self, string):
        ret = 0
        strsum = 0
        for i in range(len(string)):
            c = ord(string[i])
            strsum += c
            t1 = strsum & 0x1F
            t2 = 0x20 - t1
            t3 = (c >> t2) & 0xFF
            t4 = c << t1
            v = t3 | t4
            ret += v
        return ret & 0XFFFFFFFF

    def __readfilelist(self):
        f = open(self.__path)
        lines = f.read().splitlines()
        for l in lines:
            hash = self.__hashstring(l)
            self.__filelist[hash] = l

    @property
    def Files(self):
        return self.__filelist