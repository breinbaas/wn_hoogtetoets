from routes import Routes
from ahncutter import AHNCutter
from settings import AHNVersion

routes = Routes().routes
route2 = routes['P062_001']
ahncutter2 = AHNCutter(route2)
ahn2_tile = ahncutter2.execute(AHNVersion.AHN2)

route3 = routes['P014_004']
ahncutter3 = AHNCutter(route3)
ahn3_tile = ahncutter3.execute(AHNVersion.AHN3)

route4 = routes['A122_002']
ahncutter4 = AHNCutter(route4)
ahn4_tile = ahncutter4.execute(AHNVersion.AHN4)


EXPECTED_AHN2TILE_OUTPUT = [
    (117286.88, 464731.81, -1.695),
    (117287.05, 464731.53, -1.671)    
]

EXPECTED_AHN3TILE_OUTPUT = [
    (113256.38, 471117.44, -0.156),
    (113256.93, 471116.58, 0.029)    
]

EXPECTED_AHN4TILE_OUTPUT = [
    (125570.57, 483534.93, -0.304),
    (125570.06, 483534.05, 0.243),    
]

for x, y, z in EXPECTED_AHN2TILE_OUTPUT:
    z = f"{z:.3f}"
    zt = f"{ahn2_tile.get_z(x,y):.3f}"
    if z == zt:
        print(f"[OK] expected {z} at {x}, {y} and got {zt}")
    else:
        print(f"[ERROR] expected {z} at {x}, {y} but got {zt}")

for x, y, z in EXPECTED_AHN3TILE_OUTPUT:
    z = f"{z:.3f}"
    zt = f"{ahn3_tile.get_z(x,y):.3f}"
    if z == zt:
        print(f"[OK] expected {z} at {x}, {y} and got {zt}")
    else:
        print(f"[ERROR] expected {z} at {x}, {y} but got {zt}")

for x, y, z in EXPECTED_AHN4TILE_OUTPUT:
    z = f"{z:.3f}"
    zt = f"{ahn4_tile.get_z(x,y):.3f}"
    if z == zt:
        print(f"[OK] expected {z} at {x}, {y} and got {zt}")
    else:
        print(f"[ERROR] expected {z} at {x}, {y} but got {zt}")