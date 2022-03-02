from enum import IntEnum

# enum for ahn versions
class AHNVersion(IntEnum):
    AHN2 = 2
    AHN3 = 3
    AHN4 = 4

# convienience dict for naming the ahn tiles
AHNPREFIX = {
    AHNVersion.AHN2: "ahn2",
    AHNVersion.AHN3: "ahn3",
    AHNVersion.AHN4: "ahn4"   
}

# original AHN data
AHN2DATA = "C:/Users/brein/Documents/Waternet/Hoogtetoets/ahn2"
AHN3DATA = "C:/Users/brein/Documents/Waternet/Hoogtetoets/ahn3"
AHN4DATA = "C:/Users/brein/Documents/Waternet/Hoogtetoets/ahn4"

# minimized data (after running ahnextractor)
# MINIMIZED_AHNPATHS = {
#     AHNVersion.AHN2: "C:/Users/brein/Documents/Waternet/Hoogtetoets/hoogtetoets/ahn2_levee",
#     AHNVersion.AHN3: "C:/Users/brein/Documents/Waternet/Hoogtetoets/hoogtetoets/ahn3_levee",
#     AHNVersion.AHN4: "C:/Users/brein/Documents/Waternet/Hoogtetoets/hoogtetoets/ahn4_levee"
# }

# files with the required height and backgroundsettlement
ROUTES_SHAPEFILE = "C:/Users/brein/Documents/Waternet/Hoogtetoets/shapefiles/secundaire_keringen.shp"
DTH_SHAPEFILE = "C:/Users/brein/Documents/Waternet/Hoogtetoets/shapefiles/dtinfo.shp"
# BGS_SHAPEFILE_PATH = "C:/Users/brein/Documents/Waternet/Hoogtetoets/shapefiles"



# where to store the logfiles
#HEIGHTASSESSMENT_LOG_PATH = "C:/Users/brein/Documents/Waternet/Hoogtetoets/log"

# ahnx years
# see  
# ahn2: https://www.arcgis.com/home/item.html?id=da41b7e104e045f289f3b4099e7cb4ac#data
# ahn3: https://hwh.maps.arcgis.com/apps/CompareAnalysis/index.html?appid=b2d67e3a99cf47759d34b19476476889
# ahn4: not yet available
AHN2YEAR = 2010
AHN3YEAR = 2014
AHN4YEAR = 2020

# date to use as time = 0 to calculate settlements
ANALYSISYEAR = 2022

# maximum offset left or right of the levee, should solve problems where people
# try to get height values that do not fit in the minimized tiles
MAXOFFSET = 50

# minimum interval for steps on the referenceline as well on the offset
MININTERVAL = 0.5

# the offsets to take into account (can be any list of numbers)
# Note; make sure that 0 is part of the offsets
# the calculation will fail if it is not 
OFFSET_BACKGROUNDSETTLEMENT = (-1, 0, 1) 

# the next offset settings are used to check the height of the levee
# refline checks will require that *each point* in the offset is
# equal to or higher than the required height
# offset settings for 'green' levees (no roads)
#OFFSET_REFLINE_GREEN = 1.5 # always start from reference point to right (polder)
# offset setting for 'gray' levees (roads)
OFFSET_REFLINE_GRAY = 1.5 # always start from reference point to right (polder)

# the next offset settings are used to check the height of the levee
# over the 'kernzone' Depending on a green resp. gray levee the assessment
# checks if there is a least a zone of 1.5 resp 2.5m that is higher or equal
# to the required height
# example (-5, 20) means 5m to the left (water) of the refline and 20m to the right (polder)
OFFSET_KERNZONE = (-5, 20) 
# Note; it is also possible to set the offset in the execute function of the HeightAssessment class

# default output path for writing files
OUTPUT_PATH_SHAPEFILES = "C:/Users/brein/Documents/Waternet/Hoogtetoets/out/shapefiles"
OUTPUT_PATH_IMAGES = "C:/Users/brein/Documents/Waternet/Hoogtetoets/out/images"
OUTPUT_PATH_CSV = "C:/Users/brein/Documents/Waternet/Hoogtetoets/out/csv"
OUTPUT_PATH_LOG = "C:/Users/brein/Documents/Waternet/Hoogtetoets/out/log"

DTH_CSV_FILE = f"{OUTPUT_PATH_CSV}/dth.csv"
BGS_CSV_FILE = f"{OUTPUT_PATH_CSV}/background_settlement.csv"

FUTURES = [5, 10, 15, 20]

MAX_BGS = -0.02 

STEP_SIZE_CHAINAGE = 5 # check for the height every 5m on the levee

