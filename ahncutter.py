__author__      = "Rob van Putten"
__copyright__   = "Licensed under GPLv3"

from typing import List
import numpy as np

from tileset import Tileset
from settings import AHNVersion

class AHNTile:
    def __init__(self, data, dtcode, xmin, ymax, res, nodata):
        self.data = data
        self.dtcode = dtcode
        self.xmin = xmin
        self.ymax = ymax
        self.res = res    
        self.nodata = nodata

    def get_z(self, x, y):
        dx = x - self.xmin
        dy = self.ymax - y

        idx = int(round(dx / self.res)) - 1
        idy = int(round(dy / self.res)) - 1
        
        try:
            z = self.data[idy,idx]
            if z == self.nodata:
                return np.nan
            return z
        except:
            return np.nan

    
    def subtract(self, ahntile, delta_years) -> "AHNTile":
        data = (self.data - ahntile.data) / delta_years
        return AHNTile(
            data = data,
            dtcode = self.dtcode,
            xmin = self.xmin,
            ymax = self.ymax,
            res = self.res, 
            nodata = self.nodata,
        )

class AHNCutter:
    def __init__(self, route):
        self.route = route
        self.ahn_data = {
            AHNVersion.AHN2: Tileset(type=AHNVersion.AHN2),
            AHNVersion.AHN3: Tileset(type=AHNVersion.AHN3), 
            AHNVersion.AHN4: Tileset(type=AHNVersion.AHN4)
        }

    def execute(self, ahn_version: AHNVersion, offset=100) -> List[str]:
        # get boundary of the referenceline
        xmin, ymin, xmax, ymax = self.route.get_bounding_box()
        # and add an offset
        xmin -= offset
        ymin -= offset
        xmax += offset
        ymax += offset

        ahn_data = self.ahn_data[ahn_version]
        
        # this will only work if a levee is max 2x2 tiles which is a valid assumption (I think... ;-)    
        tile_tl = ahn_data.get_tile_by_xy(xmin, ymax)
        tile_tr = ahn_data.get_tile_by_xy(xmax, ymax)
        tile_bl = ahn_data.get_tile_by_xy(xmin, ymin)
        tile_br = ahn_data.get_tile_by_xy(xmax, ymin)

        # start with the data of the topleft tile
        if tile_tl is None:
            print(f"Could not find tiles for {self.route.name}.")            

        tile_tl._read() # force to read the data and store the data   
        data = tile_tl.data  #np.array

        # if there is another tile on the right and it is not the
        # same as tile_tl add it as a column to the final matrix
        if tile_tr != tile_tl:        
            if tile_tr is not None:
                tile_tr._read()
                data = np.hstack((data, tile_tr.data))  
            else:
                print(f"Could not find tiles for {self.route.name}.")


        # if there is another tile on the bottom..
        if tile_bl is not None and tile_bl != tile_tl:        
            tile_bl._read()        
            if tile_tr != tile_tl: # and if we already added a column..
                # then join both first horizontally (or else we could end up with a funny but invalid numpy array)
                if tile_br is not None:
                    tile_br._read()
                    bdata = np.hstack((tile_bl.data, tile_br.data))            
                else:
                    print(f"Could not find tiles for {self.route.name}.")                        
            else: # ok, just one tile so far, now just join one, no need to add the bottomright one
                bdata = tile_bl.data

            # and now add this matrix bdata as a new row to the final matrix
            data = np.vstack((data, bdata))
        
        # now limit the size of the matrix based on the boundaries
        xres, yres = tile_tl.resolution.values()
        xtl, ytl = tile_tl.boundary['left'], tile_tl.boundary['top']

        # find the index in the matrix
        idx_x1 = int((xmin - xtl) / xres)
        idx_y1 = int((ytl - ymax) / yres)
        idx_x2 = int((xmax - xtl) / xres)
        idx_y2 = int((ytl - ymin) / yres)
        
        # select the final matrix
        selection = data[idx_y1:idx_y2, idx_x1:idx_x2]

        return AHNTile(selection, self.route.name, xtl + idx_x1 * xres, ytl - idx_y1 * xres, xres, tile_tl.nodata)

