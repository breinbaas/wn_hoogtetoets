__author__      = "Rob van Putten"
__copyright__   = "Licensed under GPLv3"

import math
from statistics import mean

class Route:
    def __init__(self):
        self.name = ""
        self.geometry = None
        self.mxy = []  
        self.dth = 9999

    def mxy_to_csv(self, filename):
        fout = open(filename, 'w')
        for mxy in self.mxy:
            fout.write("%d,%.2f,%.2f\n" % (mxy[0], mxy[1], mxy[2]))
    
    @property
    def mmax(self):
        return self.mxy[-1][0]

    @property
    def mmin(self):
        return self.mxy[0][0]

    @property
    def xypoints(self):
        return [(p[1], p[2]) for p in self.mxy]

    def get_midpoint(self):
        xmid = mean([p[1] for p in self.mxy])
        ymid = mean([p[2] for p in self.mxy])
        return xmid, ymid

    def xya_at_m(self, m):
        for i in range(1, len(self.mxy)):
            m1, x1, y1 = self.mxy[i-1]
            m2, x2, y2 = self.mxy[i]

            if(m1 <= m <= m2):
                # print("m1: %.2f, m2: %.2f, x1: %.2f, y1: %.2f, x2:%.2f, y2:%.2f" % (m1,m2,x1,y1,x2,y2))
                x = x1 + (m - m1) / (m2 - m1) * (x2 - x1)
                y = y1 + (m - m1) / (m2 - m1) * (y2 - y1)
                alpha = math.atan2((y1-y2), (x1-x2))
                return x, y, alpha
                
        return 0., 0., 0.
        
    def get_bounding_box(self, margin=0.):
        result = [1e9,1e9,-1e9,-1e9] #[xmin, ymin, xmax, ymax]
        for m,x,y in self.mxy:
            if x < result[0]: result[0] = x
            if x > result[2]: result[2] = x
            if y < result[1]: result[1] = y
            if y > result[3]: result[3] = y
        return [result[0]-margin, result[1]-margin, result[2]+margin, result[3]+margin]

    

