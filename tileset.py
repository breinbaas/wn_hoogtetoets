__author__      = "Rob van Putten"
__copyright__   = "Licensed under GPLv3"

import glob, os
import rasterio as rio
import numpy as np

from settings import AHN4DATA, AHN3DATA, AHN2DATA, AHNVersion

TILESETS = {
    AHNVersion.AHN2: AHN2DATA,
    AHNVersion.AHN3: AHN3DATA,  
    AHNVersion.AHN4: AHN4DATA,
}

INI_NAME = "tiles.ini"

class Tile:
    def __init__(self):
        self.boundary = {}
        self.resolution = {}
        self.shape = {}
        self.data = None
        self.nodata = None
        self.filename = ""

    @classmethod
    def from_tif(self, filename):
        tile = Tile()

        r = rio.open(filename)
        tile.data = r.read(1, masked=True).data
        tile.boundary = {"left":r.bounds.left, "right":r.bounds.right, "bottom":r.bounds.bottom, "top":r.bounds.top}
        tile.shape = {"columns":r.meta['width'], "rows":r.meta['height']}
        tile.data = r.read(1, masked=True).data
        tile.resolution = {"x":r.res[1], "y":r.res[0]}
        tile.nodata = r.meta['nodata']
        tile.filename = filename
        return tile

    def contains_point(self, x, y):
        return x <= self.boundary['right'] and x >= self.boundary['left'] and y>= self.boundary['bottom'] and y<=self.boundary['top']
    
    def _read(self):
        if self.data is None:
            #print("[I] reading {}".format(self.filename))
            r = rio.open(self.filename)
            self.data = r.read(1, masked=True).data

    def info(self):
        print("Boundaries  : ", self.boundary)
        print("Resolutie   : ", self.resolution)
        print("Data grootte: ", self.shape)
        print("No data     : ", self.nodata)

    def get_z(self, x, y):
        self._read()
        dx = x - self.boundary['left']
        dy = self.boundary['top'] - y

        idx = int(round(dx / self.resolution['x'])) - 1
        if idx<0 or idx>=self.shape['columns']:
            return np.nan

        idy = int(round(dy / self.resolution['y'])) - 1
        if idy<0 or idy>=self.shape['rows']:
            return np.nan

        z = self.data[idy,idx]
        if z == self.nodata:
            return np.nan
        return z

class Tileset:
    def __init__(self, type=AHNVersion.AHN4):
        self._tiles = []
        self._type = type
        self._tilesdir = None
        self._inifile = None

        if self._type in TILESETS.keys():
            self._tilesdir = TILESETS[self._type]
            self._inifile = os.path.join(self._tilesdir, INI_NAME)
            self._initialize_available_data()

    def get_tile_by_xy(self, x, y):
        for tile in self._tiles:
            if tile.contains_point(x, y):
                return tile
        
        return None
        

    def setup(self):
        print(self._tilesdir)
        print("[I] Setting up ini file")
        fout = open(self._inifile, 'w')

        files = glob.glob(self._tilesdir + '/*.tif')

        if len(files)==0:
            print("No tif files found, checking for img files")
            files = glob.glob(self._tilesdir + '/*.img')

        i, itot = 1, len(files)
        fout.write('file;left;right;bottom;top;resolution_x;resolution_y;rows;columns;no_data\n')
        for file in files:
            print("[I] Handling file {} {}/{}".format(file, i, itot))
            r = rio.open(file)
            fout.write('{};{};{};{};{};{};{};{};{};{}\n'.format(file, r.bounds.left, r.bounds.right, r.bounds.bottom, r.bounds.top,
                                                 r.res[1], r.res[0], r.meta['width'], r.meta['height'], r.meta['nodata']))
            i+=1
        print("[I] Ini bestand is afgerond en opgeslagen.")
        fout.close()

    def _initialize_available_data(self):
        if self._type is None: return
        #check if an ini file is available
        if os.path.isfile(self._inifile):
            self._read_ini()
            return

        print("[W] Geen ini bestand gevonden. Gebruik de setup functie om deze te genereren.")

    def _check_ini(self):
        result = True
        fin = open(self._inifile)
        lines = fin.readlines()
        fin.close()
        for line in lines[1:]:
            args = [s.strip() for s in line.split(';')]
            if not os.path.isfile(args[0]):
                print("[E] Het bestand {} is niet beschikbaar.".format(args[0]))
                result = False
        return result

    def _read_ini(self):
        if not self._check_ini():
            print("[E] Fout in ini bestand gevonden. Verwijder het bestand en run de setup opnieuw.")
            return

        fin = open(self._inifile)
        lines = fin.readlines()
        fin.close()
        for line in lines[1:]:
            args = [s.strip() for s in line.split(';')]
            tile = Tile()
            tile.filename = args[0]
            tile.resolution['x'] = float(args[5])
            tile.resolution['y'] = float(args[6])
            tile.boundary['left'] = float(args[1]) - tile.resolution['x'] / 2.
            tile.boundary['right'] = float(args[2]) - tile.resolution['x'] / 2.
            tile.boundary['bottom'] = float(args[3]) + tile.resolution['y'] / 2.
            tile.boundary['top'] = float(args[4]) + tile.resolution['y'] / 2.
            tile.shape['columns'] = int(args[7])
            tile.shape['rows'] = int(args[8])
            tile.nodata = float(args[9])
            self._tiles.append(tile)

        #print("[I] Ini bestand is ok")

    def get_z(self, x, y):
        """Get the lowest z value in the tiles because sometimes they seem to be overlapping especially with the waterbottom"""
        result = 1e9
        for tile in self._tiles:
            if tile.boundary['left'] <= x <= tile.boundary['right'] and tile.boundary['bottom'] <= y <= tile.boundary['top']:
                z = tile.get_z(x, y) 
                if not np.isinf(z) and not np.isnan(z): #some img / tif files overlap, so only return a value if it is not None, else look further
                    if z < result:
                        result = z
        
        if result == 1e9:
            return np.nan
        else:
            return result

if __name__=="__main__":
    ts = Tileset(type=AHNVersion.AHN2)
    #print(ts.get_z(124504.22,483328.12))
    ts.setup()