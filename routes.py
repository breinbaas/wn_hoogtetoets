__author__      = "Rob van Putten"
__copyright__   = "Licensed under GPLv3"

import math
from osgeo import ogr
from route import Route

from settings import ROUTES_SHAPEFILE

class Routes:
    def __init__(self):
        self.route_file = ROUTES_SHAPEFILE
        self.routes = {}
        try:
            self._read_from_shapefile(self.route_file)
        except Exception as e:            
            print(f"Fout bij het initialiseren van de routes, verwijst DTH_SHAPEFILE={self.route_file} naar het juiste bestand?")
            print(e)
            raise

    def has_dtcode(self, code):
        return self.route_by_code(code) is not None

    def route_by_code(self, code):
        if code in self.routes.keys():
            return self.routes[code]    
        return None

    def _read_from_shapefile(self, shapefile):
        infile = ogr.Open(shapefile)
        layer = infile.GetLayer()        
        for i in range(layer.GetFeatureCount()):
            feature = layer.GetFeature(i)
            geom = feature.GetGeometryRef()
            rt = Route()
            rt.name = feature.GetField('code')
            #rt.dth = feature.GetField('dth')            
            xp, yp, m = 0., 0., 0.
            for j in range(geom.GetPointCount()):
                pt = geom.GetPoint(j)
                if j==0:
                    rt.mxy.append((0,pt[0],pt[1]))
                else:
                    dx = rt.mxy[-1][1] - pt[0]
                    dy = rt.mxy[-1][2] - pt[1]
                    m += math.sqrt(dx**2 + dy**2)
                    rt.mxy.append((m,pt[0],pt[1]))

            self.routes[rt.name] = rt      
            
    def get_dt_names(self):
        return [s for s in self.routes.keys()]

    def get_by_code(self, dtcode):
        if dtcode in self.routes.keys():
            return self.routes[dtcode]
        else:
            return None

if __name__=="__main__":
    rts = Routes()
    print(rts.get_dt_names())