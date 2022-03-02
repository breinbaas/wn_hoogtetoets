from settings import AHNVersion
from tileset import Tileset

# expected out is determined by a manuall QGis search
EXPECTED_AHN2_OUTPUT = [
    (138207.30, 465777.94, 0.547),
    (138207.48, 465777.94, 0.547),
    (138207.48, 465777.76, 0.547),
    (138207.30, 465777.76, 0.547),    
]

EXPECTED_AHN3_OUTPUT = [
    (121376.19, 488675.62, 2.979),
    (121375.78, 488675.59, 2.992),
    (121376.49, 488675.39, 3.045),
    (121375.95, 488675.39, 2.991),
]

EXPECTED_AHN4_OUTPUT = [
    (117739.71, 465961.68, -1.520),
    (117739.46, 465961.94, -1.489),
    (117739.97, 465962.46, -1.477),
    (117740.07, 465961.03, -1.494),
]

ts2 = Tileset(type=AHNVersion.AHN2)
ts3 = Tileset(type=AHNVersion.AHN3)
ts4 = Tileset(type=AHNVersion.AHN4)

for x, y, z in EXPECTED_AHN2_OUTPUT:
    z = f"{z:.3f}"
    zt = f"{ts2.get_z(x,y):.3f}"
    if z == zt:
        print(f"[OK] expected {z} at {x}, {y} and got {zt}")
    else:
        print(f"[ERROR] expected {z} at {x}, {y} but got {zt}")

for x, y, z in EXPECTED_AHN3_OUTPUT:
    z = f"{z:.3f}"
    zt = f"{ts3.get_z(x,y):.3f}"
    if z == zt:
        print(f"[OK] expected {z} at {x}, {y} and got {zt}")
    else:
        print(f"[ERROR] expected {z} at {x}, {y} but got {zt}")

for x, y, z in EXPECTED_AHN4_OUTPUT:
    z = f"{z:.3f}"
    zt = f"{ts4.get_z(x,y):.3f}"
    if z == zt:
        print(f"[OK] expected {z} at {x}, {y} and got {zt}")
    else:
        print(f"[ERROR] expected {z} at {x}, {y} but got {zt}")

