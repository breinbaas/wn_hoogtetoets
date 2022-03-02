import math

class BgsInfo:
    def __init__(self, dtcode, x, y, bgs):
        self.dtcode = dtcode
        self.x = x
        self.y = y
        self.bgs = bgs

    def __str__(self):
        return f"\ndtcode: {self.dtcode}\nx: {self.x}\ny: {self.y}\nbgs: {self.bgs}\n"

class BgsSelection:
    def __init__(self, bgs):
        self.bgs = bgs

    def get_closest(self, x, y):
        ls = [(math.hypot(x-p.x, y-p.y), p) for p in self.bgs]

        if len(ls) > 0:
            return sorted(ls, key=lambda x: x[0])[0][1]
        
        return None

class BgsData:
    def __init__(self):
        self.bgs = []

    @classmethod
    def from_file(obj, filename):
        r = BgsData()
        lines = open(filename, 'r').readlines()
        for line in lines[1:]:
            args = line.split(',')
            r.bgs.append(BgsInfo(args[0], float(args[2]), float(args[3]), float(args[5])))
        return r

    def get(self, dtcode):
      return BgsSelection([r for r in self.bgs if r.dtcode==dtcode])



