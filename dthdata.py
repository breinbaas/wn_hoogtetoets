import math

class DthInfo:
    def __init__(self, dtcode, x, y, mhw, dth, ipo):
        self.dtcode = dtcode
        self.x = x
        self.y = y
        self.mhw = mhw
        self.dth = dth
        self.ipo = ipo

    def __str__(self):
        return f"\ndtcode: {self.dtcode}\nx: {self.x}\ny: {self.y}\nmhw: {self.mhw}\ndth: {self.dth}\nipo: {self.ipo}\n"

class DthSelection:
    def __init__(self, dth):
        self.dth = dth

    def get_closest(self, x, y):
        ls = [(math.hypot(x-p.x, y-p.y), p) for p in self.dth]

        if len(ls) > 0:
            return sorted(ls, key=lambda x: x[0])[0][1]
        
        return None

class DthData:
    def __init__(self):
        self.dth = []

    @classmethod
    def from_file(obj, filename):
        r = DthData()
        lines = open(filename, 'r').readlines()
        for line in lines[1:]:
            args = line.split(',')
            r.dth.append(DthInfo(args[0], float(args[1]), float(args[2]), float(args[3]), float(args[4]), int(args[5])))
        return r

    def get(self, dtcode):
      return DthSelection([r for r in self.dth if r.dtcode==dtcode])



