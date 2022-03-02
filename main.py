from cProfile import run
from bgsdata import BgsData
from dthdata import DthData
from routes import Routes
import shapefile
from ahncutter import AHNCutter
from settings import AHN2YEAR, AHN3YEAR, AHN4YEAR, AHNVersion, OFFSET_BACKGROUNDSETTLEMENT, OUTPUT_PATH_CSV, OUTPUT_PATH_SHAPEFILES, OUTPUT_PATH_LOG, DTH_CSV_FILE, STEP_SIZE_CHAINAGE, BGS_CSV_FILE
import numpy as np
import math
import random
from tqdm import tqdm
from pathlib import Path
from pyproj import Transformer

# NOTE FOR HOME
# set PROJ_LIB path to
# D:\Development\Python\heightassessment\.env\Lib\site-packages\pyproj\proj_dir\share\proj
# and afterwards back to
# D:\Apps\PostgreSQL\12\share\contrib\postgis-3.2\proj

def calculate_bgs():
    routes = Routes().routes
    dthdata = DthData.from_file(DTH_CSV_FILE)
    fmain = open(f"{OUTPUT_PATH_CSV}/background_settlement_metadata.csv", 'w')
    fmain.write("dtcode,missing_bgs [%],positive_bgs [%]\n") 

    fbgs = open(BGS_CSV_FILE, 'w')
    fbgs.write("dtcode,chainage,x,y,z_ahn4,bgs\n")

    fbgs_flutter_app = open("flutter_bgs_data.csv", 'w')
    fbgs_flutter_app.write("dtcode,lat,lon,z_ahn4,bgs,z_req\n")

    transformer = Transformer.from_crs(28992, 4326)
        
    # select some levees for a complete 
    dtcodes_for_full_debug = random.choices(Routes().get_dt_names(), k=3)    
    for dtcode, route in tqdm(routes.items()):
        dthselection = dthdata.get(route.name)
        full_debug_output = dtcode in dtcodes_for_full_debug
        # get the relevant data
        ahncutter = AHNCutter(route)   
        try:     
            ahn2 = ahncutter.execute(AHNVersion.AHN2)
            ahn3 = ahncutter.execute(AHNVersion.AHN3)
            ahn4 = ahncutter.execute(AHNVersion.AHN4)
        except:
            fmain.write(f"{route.name},9999,9999\n")
            continue     

        if full_debug_output:
            fdebug = open(f"{OUTPUT_PATH_LOG}/{route.name}_performance_check.log", 'w')
    
        # calculate background settlement
        ahn32 = ahn3.subtract(ahn2, AHN3YEAR - AHN2YEAR)
        ahn42 = ahn4.subtract(ahn2, AHN4YEAR - AHN2YEAR)
        ahn43 = ahn4.subtract(ahn3, AHN4YEAR - AHN3YEAR)   

        chainage = np.arange(route.mmin, route.mmax, 1.0)

        if full_debug_output:
            fdebug.write(f"Background settlement per chainage for {route.name}\n")
            fdebug.write("--------------------------------------------------------------------------------\n")
            fdebug.write("chainage,  offset,  x,         y,         z42,       z43,      z32\n")
        
        num_c_with_positive_bgs, num_c_without_bgs_data = 0, 0        
        for c in chainage:
            bgs32, bgs42, bgs43 = [], [], []
            ctx,cty,a = route.xya_at_m(c)
            ctz = ahn4.get_z(ctx, cty)
            for offset in OFFSET_BACKGROUNDSETTLEMENT:  
                angle = a + math.radians(90)
                x = ctx + offset * math.cos(angle)
                y = cty + offset * math.sin(angle) 
                z32 = ahn32.get_z(x, y)
                z42 = ahn42.get_z(x, y)
                z43 = ahn43.get_z(x, y)

                if np.isinf(z32) or np.isnan(z32) or z32 < -9999 or z32 > 9999:  
                    z32 = 9999
                else:
                    bgs32.append(z32)
                if np.isinf(z42) or np.isnan(z42) or z42 < -9999 or z42 > 9999:  
                    z42 = 9999
                else:
                    bgs42.append(z42)
                if np.isinf(z43) or np.isnan(z43) or z43 < -9999 or z43 > 9999:  
                    z43 = 9999
                else:
                    bgs43.append(z43)

                if full_debug_output:
                    fdebug.write(f"{int(c):8d}, {int(offset):8d}, {x:8.2f}, {y:8.2f}, {z42:8.3f}, {z43:8.3f}, {z32:8.3f}\n")

            if len(bgs32) > 0:
                bgs32 = np.array(bgs32).mean()
            else:
                bgs32 = 9999
            
            if len(bgs42) > 0:
                bgs42 = np.array(bgs42).mean()
            else:
                bgs42 = 9999
            
            if len(bgs43) > 0:
                bgs43 = np.array(bgs43).mean()
            else:
                bgs43 = 9999

            if full_debug_output:
                fdebug.write(f"--------------------------------------------------------------------------------\n")
                fdebug.write(f"average background settlement:            {bgs42:8.3f}, {bgs43:8.3f}, {bgs32:8.3f}\n")
                
            # check if the bgs > 0, in that case make it 0.0
            if bgs43 != 9999 and bgs43 > 0:
                bgs43 = 0.0
            if bgs42 != 9999 and bgs42 > 0:
                bgs42 = 0.0
            if bgs32 != 9999 and bgs32 > 0:
                bgs32 = 0.0

            if full_debug_output:
                fdebug.write(f"after check for >0:                       {bgs42:8.3f}, {bgs43:8.3f}, {bgs32:8.3f}\n")
                
            # now choose the best bgs that is available
            final_bgs = bgs42
            if final_bgs == 9999 or final_bgs >= 0:
                final_bgs = bgs43
            if final_bgs == 9999 or final_bgs >= 0:
                final_bgs = bgs32

            if full_debug_output:
                fdebug.write(f"final bgs (ordered 42 > 43 > 32):         {final_bgs:8.3f}, {final_bgs:8.3f}, {final_bgs:8.3f}\n")
                fdebug.write("\n")

            if final_bgs == 0:
                num_c_with_positive_bgs += 1
            if final_bgs == 9999:
                num_c_without_bgs_data += 1


            if c % 5 == 0:
                dthinfo = dthselection.get_closest(ctx, cty)
                lon, lat = transformer.transform(ctx, cty)
                if dthinfo is None:
                    fbgs_flutter_app.write(f"{dtcode},{lat:.6f},{lon:.6f},{ctz:.3f},{final_bgs:.4f},9999\n")
                else:
                    fbgs_flutter_app.write(f"{dtcode},{lat:.6f},{lon:.6f},{ctz:.3f},{final_bgs:.4f},{dthinfo.dth:.2f}\n")
            
            fbgs.write(f"{dtcode},{c},{ctx:.2f},{cty:.2f},{ctz:.3f},{final_bgs:.4f}\n")
            
                
        p_without_bgs = num_c_without_bgs_data / len(chainage) * 100.0
        p_with_positive_bgs = num_c_with_positive_bgs / len(chainage) * 100.0

        fmain.write(f"{route.name},{p_without_bgs:.1f},{p_with_positive_bgs:.1f}\n")
            

        if full_debug_output:
            fdebug.write("--------------------------------------------------------------------------------\n")
            fdebug.write(f"percentage of chainages without bgs data: {p_without_bgs:3.1f}%\n")
            fdebug.write(f"percentage of chainages with bgs > 0    : {p_with_positive_bgs:3.1f}%\n")

        if full_debug_output:
            fdebug.write("--------------------------------------------------------------------------------\n")

        if full_debug_output:
            fdebug.close()

    fbgs.close()
    fmain.close()
    fbgs_flutter_app.close()

def run_height_assessment(year: int, offset_left: int=0, offset_right: int=2, reqwidth=2.0, strict=True):
    routes = Routes().routes
    dthdata = DthData.from_file(DTH_CSV_FILE)
    bgsdata = BgsData.from_file(BGS_CSV_FILE)
    suffix = f"-{offset_left}_to_{offset_right}"
    numkernzone = round(reqwidth / 0.5)

    if strict:
        fmeta = open(f"{OUTPUT_PATH_CSV}/assessment_metadata_{year}_{suffix}.csv", 'w')  
        fmeta.write("dtcode,voldoende [m],onvoldoende [m],geen gegevens [m]\n")      
    else:
        fmeta = open(f"{OUTPUT_PATH_CSV}/assessment_kernzone_metadata.csv", 'w') 
        fmeta.write("dtcode,voldoende [m],onvoldoende [m]\n")

    flog = open(f"{OUTPUT_PATH_LOG}/assessment_metadata_{year}_{suffix}.log", 'a+') 

    #for dtcode, route in tqdm(routes.items()):
    for _, route in tqdm(routes.items()):        
        chainage = np.arange(route.mmin, route.mmax, STEP_SIZE_CHAINAGE)
        ahncutter = AHNCutter(route)  
        ahn4 = ahncutter.execute(AHNVersion.AHN4) 
        dthselection = dthdata.get(route.name)
        bgsselection = bgsdata.get(route.name)

        m_voldoende = 0
        m_onvoldoende = 0
        m_nodata = 0

        # create the shapefile        
        sf_allpoints = shapefile.Writer(str(Path(OUTPUT_PATH_SHAPEFILES) / f'allpoints_{route.name}_{year}_{suffix}'))       
        sf_allpoints.field(f'z_ahn4')  
        sf_allpoints.field(f'z_{year}')   
        sf_allpoints.field(f'resultaat', 'C', 50)

        if strict:
            sf_refline_strict = shapefile.Writer(str(Path(OUTPUT_PATH_SHAPEFILES) / f'refline_strict_{route.name}_{year}_{suffix}')) 
            sf_refline_strict.field(f'dth')  
            sf_refline_strict.field(f'z_min')   
            sf_refline_strict.field(f'resultaat', 'C', 50)
        else:
            sf_refline_kernzone = shapefile.Writer(str(Path(OUTPUT_PATH_SHAPEFILES) / f'refline_kernzone_{route.name}_{year}_{suffix}')) 
            sf_refline_kernzone.field(f'resultaat', 'C', 50)
        
        cresult = []
        for c in chainage:
            # get the center point and angle
            ctx, cty, a = route.xya_at_m(c)
            # get the required height
            dthinfo = dthselection.get_closest(ctx, cty)
            if dthinfo is None:
                flog.write(f"route: {route.name} chainage: {c} Could not find dijktafelhoogte information.\n")
                continue

            bgsinfo = bgsselection.get_closest(ctx, cty)
            if bgsinfo is None:
                flog.write(f"route: {route.name} chainage: {c} Could not find background settlement information.\n")
                continue

            # strict method cannot have any point without data
            no_data_points = False

            zs = []
            for offset in np.arange(-offset_left, offset_right + 0.01, 0.5):
                angle = a + math.radians(90)
                x = ctx + offset * math.cos(angle)
                y = cty + offset * math.sin(angle)
                z = ahn4.get_z(x, y)
                zbg = z + bgsinfo.bgs * (year - 2021)
                zs.append(zbg)

                sf_allpoints.point(x, y)
                if np.isnan(z) or np.isinf(z):
                    sf_allpoints.record(z, zbg, 'geen gegevens')
                    no_data_points = True                     
                elif zbg < dthinfo.dth:
                    sf_allpoints.record(z, zbg, 'onvoldoende')
                else:
                    sf_allpoints.record(z, zbg, 'voldoende')

            zmin = min(zs)                
            if strict:
                # looking strict -> every point should be >= dth
                # and no point can have no data
                sf_refline_strict.point(ctx, cty)
                
                if np.isnan(zmin) or np.isinf(zmin) or no_data_points:
                    sf_refline_strict.record(dthinfo.dth, zmin, "geen gegevens")
                    m_nodata += STEP_SIZE_CHAINAGE
                elif min(zs) < dthinfo.dth:
                    sf_refline_strict.record(dthinfo.dth, zmin, "onvoldoende")
                    m_onvoldoende += STEP_SIZE_CHAINAGE
                else:
                    sf_refline_strict.record(dthinfo.dth, zmin, "voldoende")
                    m_voldoende += STEP_SIZE_CHAINAGE
            else:
                sf_refline_kernzone.point(ctx, cty)
                # not looking strict -> there should be at least n meters of consecutive points >= dth
                zbs = np.array(zs) >= dthinfo.dth
                cv = np.diff(np.where(np.concatenate(([zbs[0]], zbs[:-1] != zbs[1:], [True])))[0])[::2]
                
                if len(cv) > 0 and max(cv) >= numkernzone:
                    sf_refline_kernzone.record("voldoende")   
                    m_voldoende += STEP_SIZE_CHAINAGE                 
                else:
                    sf_refline_kernzone.record("onvoldoende")
                    m_onvoldoende += STEP_SIZE_CHAINAGE
            
            cresult.append((c,ctx,cty,dthinfo.dth,zs))
        
        if strict:
            sf_refline_strict.close()     
            fmeta.write(f"{route.name},{m_voldoende},{m_onvoldoende},{m_nodata}\n")       
        else:
            sf_refline_kernzone.close()
            fmeta.write(f"{route.name},{m_voldoende},{m_onvoldoende}\n")
        
        
        sf_allpoints.close()         

    fmeta.close()    
    flog.close()    

if __name__ == "__main__":
    #calculate_bgs()
    run_height_assessment(2030, offset_left=0, offset_right=2, strict=True)
    #run_height_assessment(2027, offset_left=0, offset_right=20, strict=False)
    