from osgeo import ogr
import math
import numpy as np
from tqdm import tqdm
from settings import DTH_SHAPEFILE, DTH_CSV_FILE

infile = ogr.Open(DTH_SHAPEFILE)
layer = infile.GetLayer()        

result = [] #x, y, dtcode, mhw, dth, ipo
for i in tqdm(range(layer.GetFeatureCount())):
    feature = layer.GetFeature(i)
    mhw = feature.GetField('mhw')
    dth = feature.GetField('dth')
    ipo = feature.GetField('ipo')
    dtcode = feature.GetField('dtcode').upper()

    if dtcode.find('_') > 0:
        dtcode = dtcode.split('_')[0]
    
    geom = feature.GetGeometryRef()    

    for j in range(1, geom.GetPointCount()):
        p1 = geom.GetPoint(j-1)
        p2 = geom.GetPoint(j)
        x1, y1 = p1[0], p1[1]
        x2, y2 = p2[0], p2[1]
        
        dx = x2 - x1
        dy = y2 - y1
        dl = math.hypot(dx, dy)
        ls = np.arange(0, dl, 10)
        for l in ls:
            x = x1 + (l / dl) * dx
            y = y1 + (l / dl) * dy
            result.append((dtcode,x,y,mhw,dth,ipo))

f = open(DTH_CSV_FILE, 'w')
f.write("dtcode,x,y,mhw,dth,ipo\n")
for r in result:
    f.write(f"{r[0]},{r[1]:.2f},{r[2]:.2f},{r[3]},{r[4]},{r[5]}\n")
f.close()