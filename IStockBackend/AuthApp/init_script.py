from AuthApp.models import Department, Unit, Volume, Subvolume
from StandardApp.models import IPSSTitle, RSNVolume, RSNGroup
from DrawingApp.models import DrawingFile, Drawing
import os
from core.utility import get_file_name_and_extension, extract_drawing_type_number, Syserror
from pathlib import Path
import json

def create_volume():
    volume_list = [
        {
            "volume_id": 1,
            "name": "FITS AND TOLERANCE"
        },
        {
            "volume_id": 2,
            "name": "ENGINEERING MATERIALS"
        },
        {
            "volume_id": 3,
            "name": "MACHINE ELEMENTS AND MECHANISM"
        },
        {
            "volume_id": 4,
            "name": "PIPES AND VESSELS"
        },
        {
            "volume_id": 5,
            "name": "CRANES AND HAND"
        },
        {
            "volume_id": 6,
            "name": "WORKSHOP PRACTICES AND EQUIPMENT"
        },
        {
            "volume_id": 7,
            "name": "COMPRESSORS PUMPS AND HYDRAULIC EQUIPMENT"
        },
        {
            "volume_id": 8,
            "name": "ELECTRICAL"
        },
        {
            "volume_id": 9,
            "name": "ELECTRICAL, MACHINE ELEMENTS AND MECHANISM"
        },
        {
            "volume_id": 10,
            "name": "PIPES AND VESSELS AND FITTINGS OF PIPE COATING PLANT"
        }
    ]

    for i in volume_list:
        name = i["name"]
        volume_id = i["volume_id"]
        Volume.objects.update_or_create(volume_id=volume_id, defaults={"name": name})


    sub_volume_list = [
        {
            "volume_id": 3,
            "sub_volume_no": "3.01",
            "name": "THREADED FASTNERS-GENERAL DESCRIPTION, PROPERTIES, TECHNICAL CONDITIONS OF SUPPLY, USES & LIMITATIONS ETC."
        },
        {
            "volume_id": 3,
            "sub_volume_no": "3.02",
            "name": "THREADED FASTNERS-DETS DETAILED DIMENSIONS FOR INDIVIDUAL TYPES FOR DIFFERENT SIZES."
        },
        {
            "volume_id": 3,
            "sub_volume_no": "3.03",
            "name": "SECURING DEVICES-WASHERS, CIRCLIPS, SPLIT PINS, LOCK NUTS ETC."
        },
        {
            "volume_id": 3,
            "sub_volume_no": "3.04",
            "name": "PINS & CUTTERS TAPER, CYLINDRICAL, SLIT PINS, NAILS,SLIT SALEEVS ETC."
        },
        {
            "volume_id": 3,
            "sub_volume_no": "3.05",
            "name": "RIVETS"
        },
        {
            "volume_id": 3,
            "sub_volume_no": "3.06",
            "name": "KEYS & SPLINED SHAFTS"
        },
        {
            "volume_id": 3,
            "sub_volume_no": "3.10",
            "name": "SHAFTS COUPLING (DISC)"
        },
        {
            "volume_id": 3,
            "sub_volume_no": "3.11",
            "name": "GEARS & GEAR BOXES"
        },
        {
            "volume_id": 3,
            "sub_volume_no": "3.12",
            "name": "TRANSMISSION BELTS & PULLEYS"
        },
        {
            "volume_id": 3,
            "sub_volume_no": "3.13",
            "name": "CHAINS & SPROCKETS"
        },
        {
            "volume_id": 3,
            "sub_volume_no": "3.14",
            "name": "TRAVELLING WHEELS AND AXLES"
        },
        {
            "volume_id": 3,
            "sub_volume_no": "3.15",
            "name": "ROPE & ROPE PULLEYS SPRINGS"
        },
        {
            "volume_id": 3,
            "sub_volume_no": "3.20",
            "name": "BEARINGS-SLIDING"
        },
        {
            "volume_id": 3,
            "sub_volume_no": "3.30",
            "name": "BEARING-ANTIFRICTION"
        },
        {
            "volume_id": 3,
            "sub_volume_no": "3.31",
            "name": "PLUMMER BLOCKS"
        },
        {
            "volume_id": 3,
            "sub_volume_no": "3.32",
            "name": "SEALS & PACKINGS"
        },
        {
            "volume_id": 3,
            "sub_volume_no": "3.33",
            "name": "LUBRICATION PIPES & FITTINGS(FILTER)"
        },
        {
            "volume_id": 3,
            "sub_volume_no": "3.34",
            "name": "GENERAL SERVICES PARTS"
        },
        {
            "volume_id": 3,
            "sub_volume_no": "3.40",
            "name": "RAILS, COVERS ,HAND,WHEELS,HANDELS ETC."
        },
        {
            "volume_id": 3,
            "sub_volume_no": "3.50",
            "name": "OIL COOLER & GAS COOLER"
        },
        {
            "volume_id": 3,
            "sub_volume_no": "3.60",
            "name": "MISC EQUIPMENTS"
        },
        {
            "volume_id": 2,
            "sub_volume_no": "2.01",
            "name": "GENERAL-MATERIAL DESIGNATION AND TESTING"
        },
        {
            "volume_id": 2,
            "sub_volume_no": "2.02",
            "name": "IRON & STEEL COMPOSITION, PROPERTIES AND USES OF PLAIN CARBON AND ALLOY STEELS, CASTINGS ETC"
        },
        {
            "volume_id": 2,
            "sub_volume_no": "2.03",
            "name": "ROLLED STEEL-FORMS , PROPERTIES OF VARIOUS STEEL SECTIONS & PLATES"
        },
        {
            "volume_id": 2,
            "sub_volume_no": "2.04",
            "name": "BRIGHT STEEL - DRAWN , TURNED POLISHED ETC. VARIOUS SECTIONS & PROPERTIES"
        },
        {
            "volume_id": 2,
            "sub_volume_no": "2.10",
            "name": "NON- FERROUS METALS- COMPOSITION, PROPERTIES & USES OF NON -FERROUS METALS & ALLOYS"
        },
        {
            "volume_id": 4,
            "sub_volume_no": "4.01",
            "name": "PIPES -GENERAL.TERMS OR DELIVERY, PRESSURE RATING, SYMBOLS AND COLOUR CODE, WELDING, FLOW AND THICKNESS CALCULATIONS, NOMOGRAMS ETC."
        },
        {
            "volume_id": 4,
            "sub_volume_no": "4.02",
            "name": "PIPES DIMENSIONS & WEIGHT"
        },
        {
            "volume_id": 4,
            "sub_volume_no": "4.03",
            "name": "SUPPORTS-BRACKETS, CLAMPS HANGERS ETC."
        },
        {
            "volume_id": 4,
            "sub_volume_no": "4.04",
            "name": "EXPANSION JOINTS"
        },
        {
            "volume_id": 4,
            "sub_volume_no": "4.05",
            "name": "FLANGES & GASKETS"
        },
        {
            "volume_id": 5,
            "sub_volume_no": "5.01",
            "name": "CRANES(MECHANICAL) FUNDAMENTAL"
        },
        {
            "volume_id": 5,
            "sub_volume_no": "5.02",
            "name": "CRANES TRANSMISSION SYSTEM AND ACCESSORIES."
        },
        {
            "volume_id": 5,
            "sub_volume_no": "5.03",
            "name": "CRANES -COUPLINGS, BRAKES & UNIVERSAL SHAFTS"
        },
        {
            "volume_id": 5,
            "sub_volume_no": "5.04",
            "name": "CRANE-HOOKS, SHEAVE BLOCK"
        },
        {
            "volume_id": 5,
            "sub_volume_no": "5.05",
            "name": "CRANES WHEELS & RAILS"
        },
        {
            "volume_id": 6,
            "sub_volume_no": "6.01",
            "name": "CUTTING PROCESSES-GENERAL. ERECTION STANDARDS FOR MACHINE TOOLS, PAINTING, LUBRICATION, INSTRUTIONS, ACCEPTANCES CONDITIONS"
        },
        {
            "volume_id": 1,
            "sub_volume_no": "1.05",
            "name": "FITS & TOLERANCE GAUGE ETC"
        },
        {
            "volume_id": 2,
            "sub_volume_no": "2.11",
            "name": "NON-FERROUS SECTIONS-FORMS AND PROPERTIES"
        },
        {
            "volume_id": 2,
            "sub_volume_no": "2.20",
            "name": "NONMETALLIC MATERIALS"
        },
        {
            "volume_id": 4,
            "sub_volume_no": "4.06",
            "name": "VALVES AND ACCESSORIES"
        },
        {
            "volume_id": 4,
            "sub_volume_no": "4.07",
            "name": "FITTINGS-STEEL"
        },
        {
            "volume_id": 4,
            "sub_volume_no": "4.08",
            "name": "FITTINGS-MALLEABLE IRON"
        },
        {
            "volume_id": 4,
            "sub_volume_no": "4.09",
            "name": "FITTINGS-NONFERROUS METAL"
        },
        {
            "volume_id": 4,
            "sub_volume_no": "4.10",
            "name": "HOSES & CLAMPS"
        },
        {
            "volume_id": 4,
            "sub_volume_no": "4.20",
            "name": "INDICATORS & METERS"
        },
        {
            "volume_id": 4,
            "sub_volume_no": "4.30",
            "name": "STORAGE  VESSELS"
        },
        {
            "volume_id": 4,
            "sub_volume_no": "4.40",
            "name": "PRESSURE VESSELS"
        },
        {
            "volume_id": 4,
            "sub_volume_no": "4.50",
            "name": "HEAT EXCHANGERS"
        },
        {
            "volume_id": 5,
            "sub_volume_no": "5.06",
            "name": "WIRE ROPES AND ACCESS ORIES"
        },
        {
            "volume_id": 5,
            "sub_volume_no": "5.07",
            "name": "GENERAL SERVICE PARTS ,BUFFERS, PLATFORMS,STAIRS,CABINS ETC"
        },
        {
            "volume_id": 5,
            "sub_volume_no": "5.30",
            "name": "CRANES(ELECTRICAL)-FUNDAMENTALS"
        },
        {
            "volume_id": 5,
            "sub_volume_no": "5.31",
            "name": "MAIN & AUXILIARY CIRCUITS"
        },
        {
            "volume_id": 5,
            "sub_volume_no": "5.32",
            "name": "LIFTING MAGNETS"
        },
        {
            "volume_id": 5,
            "sub_volume_no": "5.33",
            "name": "POWER FEEDERS"
        },
        {
            "volume_id": 5,
            "sub_volume_no": "5.34",
            "name": "WARNING & SIGNALLING EQUIPMENT"
        },
        {
            "volume_id": 5,
            "sub_volume_no": "5.50",
            "name": "GENERAL LIFTING TACKLES & WINCHES"
        },
        {
            "volume_id": 5,
            "sub_volume_no": "5.51",
            "name": "FLOOR TRANSPORT EQUIPMENT"
        },
        {
            "volume_id": 5,
            "sub_volume_no": "5.52",
            "name": "ROAD TRANSPORT"
        },
        {
            "volume_id": 5,
            "sub_volume_no": "5.53",
            "name": "ROLLING STOCK"
        },
        {
            "volume_id": 5,
            "sub_volume_no": "5.70",
            "name": "CONVEYORS & ELEVATORS"
        },
        {
            "volume_id": 6,
            "sub_volume_no": "6.20",
            "name": "HAND TOOLS"
        },
        {
            "volume_id": 6,
            "sub_volume_no": "6.30",
            "name": "HAND MACHINE TOOLSPNEUMATIC & ELECTRIC"
        },
        {
            "volume_id": 6,
            "sub_volume_no": "6.40",
            "name": "MEASURING TOOLS"
        },
        {
            "volume_id": 6,
            "sub_volume_no": "6.50",
            "name": "WELDING PROCESS-GENERAL"
        },
        {
            "volume_id": 6,
            "sub_volume_no": "6.51",
            "name": "WELDING PROCESS-DESIGN GUIDELINES"
        },
        {
            "volume_id": 6,
            "sub_volume_no": "6.52",
            "name": "WELDING & CUTTING TORCHES"
        },
        {
            "volume_id": 6,
            "sub_volume_no": "6.53",
            "name": "WELDING ELECTRODES & OTHER MATERIALS"
        },
        {
            "volume_id": 6,
            "sub_volume_no": "6.54",
            "name": "WELDING MACHINES & ACCESSORIES"
        },
        {
            "volume_id": 6,
            "sub_volume_no": "6.55",
            "name": "SAFETY APPLIANCES"
        },
        {
            "volume_id": 6,
            "sub_volume_no": "6.56",
            "name": "APPLIANCES-CYLINDER,GUAGES,HOSES,ELECTRODE HOLDERS ETC"
        },
        {
            "volume_id": 6,
            "sub_volume_no": "6.57",
            "name": "TESTING"
        },
        {
            "volume_id": 6,
            "sub_volume_no": "6.70",
            "name": "OFFICE & SHOP EQUIPMENTS WARD ROBES,FILLING CABINETS,MARKING BENCHES ETCSUNA"
        },
        {
            "volume_id": 7,
            "sub_volume_no": "7.06",
            "name": "TURBINE"
        },
        {
            "volume_id": 7,
            "sub_volume_no": "7.07",
            "name": "HYDRAULIC FILTER"
        },
        {
            "volume_id": 7,
            "sub_volume_no": "7.08",
            "name": "SEAL & PLUNGER"
        },
        {
            "volume_id": 7,
            "sub_volume_no": "7.10",
            "name": "HYDRAULIC JACKS"
        },
        {
            "volume_id": 7,
            "sub_volume_no": "7.11",
            "name": "HIGH PRESSURE PIPING & FITTINGS"
        },
        {
            "volume_id": 7,
            "sub_volume_no": "7.12",
            "name": "HYDRAULIC VALVES"
        },
        {
            "volume_id": 7,
            "sub_volume_no": "7.20",
            "name": "CRUSHERS"
        },
        {
            "volume_id": 7,
            "sub_volume_no": "7.21",
            "name": "SCREENS"
        },
        {
            "volume_id": 7,
            "sub_volume_no": "7.30",
            "name": "MISC.EQUIPMENTS"
        },
        {
            "volume_id": 6,
            "sub_volume_no": "6.02",
            "name": "MACHINE TOOLS"
        },
        {
            "volume_id": 6,
            "sub_volume_no": "6.03",
            "name": "CUTTING TOOLS"
        },
        {
            "volume_id": 6,
            "sub_volume_no": "6.04",
            "name": "JIGS & FIXTURES"
        },
        {
            "volume_id": 6,
            "sub_volume_no": "6.05",
            "name": "WOOD WORKING & SPECIAL MACHINE"
        },
        {
            "volume_id": 7,
            "sub_volume_no": "7.01",
            "name": "FANS & BLOWERS & CYCLONES"
        },
        {
            "volume_id": 7,
            "sub_volume_no": "7.02",
            "name": "BOOSTERS & COMPRESSORS"
        },
        {
            "volume_id": 7,
            "sub_volume_no": "7.03",
            "name": "RECIPROCATING PUMPS"
        },
        {
            "volume_id": 7,
            "sub_volume_no": "7.04",
            "name": "ROTARY PUMPS"
        },
        {
            "volume_id": 7,
            "sub_volume_no": "7.05",
            "name": "HYDRO PNEUMATIC CYLINDERS TURBINE"
        },
        {
            "volume_id": 1,
            "sub_volume_no": "1.01",
            "name": "INSTRUCTION FOR THE ADJUSTMENT"
        },
        {
            "volume_id": 8,
            "sub_volume_no": "8.00",
            "name": "ELECTRICAL"
        },
        {
            "volume_id": 9,
            "sub_volume_no": "8.30",
            "name": "CARBON BRUSH"
        },
        {
            "volume_id": 10,
            "sub_volume_no": "4.51",
            "name": "PIPE COATING ITEMS, TYRE"
        }
    ]

    for i in sub_volume_list:
        name = i["name"]
        volume_id = i["volume_id"]
        sub_volume_no = i["sub_volume_no"]
        if volume := Volume.objects.get(volume_id = volume_id):
            Subvolume.objects.update_or_create(volume=volume, sub_volume_no=sub_volume_no, defaults={"name": name})

def create_department():
    department_list = [
        {"department_id": 455,"name": "AC"},
        {"department_id": 428,"name": "ADMN"},
        {"department_id": 6,"name": "BARSUAN IRON MINES"},
        {"department_id": 367,"name": "BF"},
        {"department_id": 449,"name": "BF-V"},
        {"department_id": 466,"name": "BOLANI ORE MINES"},
        {"department_id": 211,"name": "BSM"},
        {"department_id": 11,"name": "C&IT"},
        {"department_id": 441,"name": "C.E.T."},
        {"department_id": 213,"name": "CCD"},
        {"department_id": 369,"name": "CE(S)"},
        {"department_id": 22,"name": "CED"},
        {"department_id": 461,"name": "CEO"},
        {"department_id": 23,"name": "CMMS"},
        {"department_id": 291,"name": "CO"},
        {"department_id": 457,"name": "CP-1"},
        {"department_id": 292,"name": "CP-2"},
        {"department_id": 28,"name": "CPP-1"},
        {"department_id": 459,"name": "CRANE MAINT."},
        {"department_id": 226,"name": "CRANES"},
        {"department_id": 395,"name": "CRM"},
        {"department_id": 34,"name": "CRO (O)"},
        {"department_id": 36,"name": "DESIGN"},
        {"department_id": 373,"name": "ED(W)"},
        {"department_id": 38,"name": "EED"},
        {"department_id": 39,"name": "EMD"},
        {"department_id": 42,"name": "ENV. ENGG. DEPT"},
        {"department_id": 235,"name": "ERWPP"},
        {"department_id": 263,"name": "ESM"},
        {"department_id": 444,"name": "F&A"},
        {"department_id": 309,"name": "FABSHOP"},
        {"department_id": 308,"name": "FM(M)"},
        {"department_id": 366,"name": "FOUNDRIES"},
        {"department_id": 53,"name": "FP"},
        {"department_id": 54,"name": "FS"},
        {"department_id": 434,"name": "G.FACILITY"},
        {"department_id": 59,"name": "GIF"},
        {"department_id": 61,"name": "HM(E)"},
        {"department_id": 180,"name": "HRDC"},
        {"department_id": 439,"name": "HRM"},
        {"department_id": 365,"name": "HSM"},
        {"department_id": 456,"name": "HSM-2"},
        {"department_id": 330,"name": "INST"},
        {"department_id": 445,"name": "INSTRUMENTATION"},
        {"department_id": 212,"name": "LDBP"},
        {"department_id": 403,"name": "Mechanical Maint."},
        {"department_id": 460,"name": "MECHANICAL SHOP"},
        {"department_id": 436,"name": "MILLS GENERAL"},
        {"department_id": 463,"name": "MINES"},
        {"department_id": 183,"name": "MM"},
        {"department_id": 125,"name": "MRD"},
        {"department_id": 462,"name": "MS"},
        {"department_id": 311,"name": "MSS"},
        {"department_id": 453,"name": "NEW CCD"},
        {"department_id": 452,"name": "NEW PLATE MILL"},
        {"department_id": 435,"name": "NSPCL"},
        {"department_id": 83,"name": "OMQ"},
        {"department_id": 464,"name": "OXYGEN PLANT"},
        {"department_id": 269,"name": "P&A"},
        {"department_id": 86,"name": "PC(S)"},
        {"department_id": 271,"name": "PD"},
        {"department_id": 465,"name": "PIPE COATING PLANT"},
        {"department_id": 92,"name": "PLDQ"},
        {"department_id": 237,"name": "PM"},
        {"department_id": 95,"name": "PPC"},
        {"department_id": 242,"name": "PROJECTS"},
        {"department_id": 97,"name": "R & C LAB"},
        {"department_id": 266,"name": "R.M.H.P"},
        {"department_id": 450,"name": "R.M.H.P-III"},
        {"department_id": 98,"name": "RC(M)"},
        {"department_id": 458,"name": "RDCIS"},
        {"department_id": 195,"name": "REFRACTORY"},
        {"department_id": 446,"name": "Repair Constn(M)"},
        {"department_id": 438,"name": "ROLLING MILL"},
        {"department_id": 107,"name": "RS(E)"},
        {"department_id": 451,"name": "RSP"},
        {"department_id": 210,"name": "RTS"},
        {"department_id": 392,"name": "SAFETY"},
        {"department_id": 454,"name": "SATNA MINES"},
        {"department_id": 114,"name": "SGP"},
        {"department_id": 432,"name": "SHOPS"},
        {"department_id": 371,"name": "SMS-1"},
        {"department_id": 368,"name": "SMS-2"},
        {"department_id": 240,"name": "SP -2"},
        {"department_id": 239,"name": "SP-1"},
        {"department_id": 448,"name": "SP-III"},
        {"department_id": 288,"name": "SPP"},
        {"department_id": 377,"name": "SSD"},
        {"department_id": 287,"name": "SSM"},
        {"department_id": 297,"name": "STORES"},
        {"department_id": 363,"name": "SWPP"},
        {"department_id": 437,"name": "TBDB"},
        {"department_id": 390,"name": "TE/TS"},
        {"department_id": 337,"name": "TOP- I"},
        {"department_id": 238,"name": "TOP-1"},
        {"department_id": 214,"name": "TOP-2"},
        {"department_id": 442,"name": "Transport"},
        {"department_id": 142,"name": "TRM"},
        {"department_id": 405,"name": "Utility"},
        {"department_id": 467,"name": "VIGILANCE"},
        {"department_id": 333,"name": "WMD" }
    ]

    for i in department_list:
        name = i["name"]
        department_id = i["department_id"]
        Department.objects.update_or_create(
            department_id=department_id, defaults={"name": name}
        )

def create_unit():
    unit_list = [
        {"unit_id": 3, "name": "150T.CONVERT"},
        {"unit_id": 4, "name": "2S T.MILL"},
        {"unit_id": 5, "name": "4 H.R.MILL"},
        {"unit_id": 6, "name": "4.H.L.MILL"},
        {"unit_id": 7, "name": "4H REVERSING"},
        {"unit_id": 8, "name": "4H.R.LINE"},
        {"unit_id": 9, "name": "4H.R.MILL"},
        {"unit_id": 11, "name": "5S STAND"},
        {"unit_id": 12, "name": "5S T MILL"},
        {"unit_id": 13, "name": "5S TAND.MILL"},
        {"unit_id": 14, "name": "5S.TANDEM"},
        {"unit_id": 15, "name": "5T TANDEM"},
        {"unit_id": 16, "name": "A NITRATE"},
        {"unit_id": 18, "name": "A&P LINE"},
        {"unit_id": 19, "name": "A&R SULPHATE"},
        {"unit_id": 20, "name": "A.C.UNIT"},
        {"unit_id": 21, "name": "A.C.W.SYSTEM"},
        {"unit_id": 22, "name": "A.COMPRESSOR"},
        {"unit_id": 23, "name": "A.FEEDER"},
        {"unit_id": 24, "name": "A.NITRATE"},
        {"unit_id": 25, "name": "A.P.C.M/C"},
        {"unit_id": 26, "name": "A.P.CUT.M/C"},
        {"unit_id": 27, "name": "A.P.HEATER"},
        {"unit_id": 28, "name": "A.P.LINE"},
        {"unit_id": 29, "name": "A.P.SYSTEM"},
        {"unit_id": 30, "name": "A.R&S PLANT"},
        {"unit_id": 31, "name": "A.R.STATION"},
        {"unit_id": 32, "name": "A.R.SULPHET"},
        {"unit_id": 33, "name": "A.R.SYSTEM"},
        {"unit_id": 34, "name": "A.RECOVERY"},
        {"unit_id": 35, "name": "A.S.TANKS"},
        {"unit_id": 36, "name": "A.S.U"},
        {"unit_id": 38, "name": "A.STAND"},
        {"unit_id": 39, "name": "A.SULPHATE"},
        {"unit_id": 40, "name": "A/C"},
        {"unit_id": 41, "name": "A/C & VENT"},
        {"unit_id": 42, "name": "A/C PLANT"},
        {"unit_id": 43, "name": "A/C SYSTEM"},
        {"unit_id": 45, "name": "ACETYLENE"},
        {"unit_id": 47, "name": "ACID PUMP"},
        {"unit_id": 46, "name": "ACID REGENERATION PLANT"},
        {"unit_id": 48, "name": "ACID TANK"},
        {"unit_id": 49, "name": "AIR COMPR"},
        {"unit_id": 50, "name": "AIR COMPRESS"},
        {"unit_id": 51, "name": "AIR SAPARATE"},
        {"unit_id": 52, "name": "AIR STATION"},
        {"unit_id": 1432, "name": "AIR SYSTEM"},
        {"unit_id": 53, "name": "AIR WASHER"},
        {"unit_id": 54, "name": "ALIGN STAND"},
        {"unit_id": 1463, "name": "ALTP-B"},
        {"unit_id": 55, "name": "AMMONIA"},
        {"unit_id": 56, "name": "AMMONIA SUL"},
        {"unit_id": 1422, "name": "AMMONIA SULPHATE PLANT"},
        {"unit_id": 57, "name": "AMONIA PLANT"},
        {"unit_id": 58, "name": "ANNEAL BASE"},
        {"unit_id": 59, "name": "ANNEAL HOOD"},
        {"unit_id": 60, "name": "ANNEAL PLANT"},
        {"unit_id": 61, "name": "ANNEALING"},
        {"unit_id": 62, "name": "APRON FEEDER"},
        {"unit_id": 63, "name": "AR & S PLANT"},
        {"unit_id": 64, "name": "ARC FCE"},
        {"unit_id": 65, "name": "ARC FURNACE"},
        {"unit_id": 66, "name": "ARCHIVES"},
        {"unit_id": 67, "name": "AREA LAB."},
        {"unit_id": 68, "name": "ARGON COMPR"},
        {"unit_id": 69, "name": "ARS"},
        {"unit_id": 70, "name": "ASH HANDLING"},
        {"unit_id": 71, "name": "ASU"},
        {"unit_id": 72, "name": "ASU-1"},
        {"unit_id": 73, "name": "ASU-1&2"},
        {"unit_id": 74, "name": "ASU-4"},
        {"unit_id": 75, "name": "ATP"},
        {"unit_id": 37, "name": "AUSTENITISING FURNACE"},
        {"unit_id": 76, "name": "AUTO CUTTING"},
        {"unit_id": 77, "name": "AUX PUMP"},
        {"unit_id": 78, "name": "AUXILIARY"},
        {"unit_id": 10, "name": "AUXILIARY CIVIL"},
        {"unit_id": 79, "name": "B&H ASSEMBLY"},
        {"unit_id": 80, "name": "B.FEED PUMP"},
        {"unit_id": 81, "name": "B.G.M/C"},
        {"unit_id": 82, "name": "B.H"},
        {"unit_id": 83, "name": "B.H.S.VALVE"},
        {"unit_id": 84, "name": "B.HEATING"},
        {"unit_id": 85, "name": "B.O.D PLANT"},
        {"unit_id": 86, "name": "B.OIL BURNER"},
        {"unit_id": 87, "name": "B.P.-5&6"},
        {"unit_id": 88, "name": "B.PLANT"},
        {"unit_id": 89, "name": "B.PRESS"},
        {"unit_id": 90, "name": "B.R.& DRIVE"},
        {"unit_id": 91, "name": "B.RECLAIMER"},
        {"unit_id": 92, "name": "B.V.PUMP"},
        {"unit_id": 93, "name": "B.W.R"},
        {"unit_id": 94, "name": "BACKUP CHOCK"},
        {"unit_id": 95, "name": "BACKUP PLANT"},
        {"unit_id": 96, "name": "BAGGING"},
        {"unit_id": 97, "name": "BALING PRESS"},
        {"unit_id": 98, "name": "BALST HEAT"},
        {"unit_id": 99, "name": "BASE FAN"},
        {"unit_id": 100, "name": "BASE PLATE"},
        {"unit_id": 101, "name": "BATT-4"},
        {"unit_id": 1368, "name": "BATTERY"},
        {"unit_id": 1424, "name": "BATTERY PROPER"},
        {"unit_id": 1484, "name": "BATTERY#3"},
        {"unit_id": 1485, "name": "BATTERY#6"},
        {"unit_id": 168, "name": "BELL WINCH"},
        {"unit_id": 102, "name": "BELL&HOPPER"},
        {"unit_id": 103, "name": "BELT C.ROOM"},
        {"unit_id": 1433, "name": "BELT CONVEYOR"},
        {"unit_id": 104, "name": "BEND STAND"},
        {"unit_id": 105, "name": "BENDING"},
        {"unit_id": 106, "name": "BENDING STND"},
        {"unit_id": 107, "name": "BEVELING M/C"},
        {"unit_id": 108, "name": "BF"},
        {"unit_id": 1456, "name": "BF-IV"},
        {"unit_id": 110, "name": "BF-PUMPHOUSE"},
        {"unit_id": 1449, "name": "BF-V"},
        {"unit_id": 109, "name": "BF.LAB"},
        {"unit_id": 111, "name": "BIM"},
        {"unit_id": 112, "name": "BINS&BUNKER"},
        {"unit_id": 1, "name": "BLANK"},
        {"unit_id": 113, "name": "BLAST HEAT"},
        {"unit_id": 1510, "name": "BLASTER TURBINE"},
        {"unit_id": 1489, "name": "BLASTING MACHINE"},
        {"unit_id": 114, "name": "BLDG&LAYOUT"},
        {"unit_id": 115, "name": "BLENDING"},
        {"unit_id": 116, "name": "BLOWER HOUSE"},
        {"unit_id": 117, "name": "BLT"},
        {"unit_id": 118, "name": "BLT D.C."},
        {"unit_id": 119, "name": "BLT EQPT"},
        {"unit_id": 120, "name": "BLT GENERAL"},
        {"unit_id": 127, "name": "BLT-COOLING"},
        {"unit_id": 128, "name": "BLT-EQPT."},
        {"unit_id": 129, "name": "BLT-ERECTION"},
        {"unit_id": 130, "name": "BLT-FCE.SHEL"},
        {"unit_id": 131, "name": "BLT-G.A"},
        {"unit_id": 132, "name": "BLT-HANDLING"},
        {"unit_id": 133, "name": "BLT-INCL.SKP"},
        {"unit_id": 134, "name": "BLT-LUB."},
        {"unit_id": 135, "name": "BLT-STRUC."},
        {"unit_id": 121, "name": "BLT. UPTAKE"},
        {"unit_id": 122, "name": "BLT.COOLING"},
        {"unit_id": 123, "name": "BLT.F.C.SYS."},
        {"unit_id": 124, "name": "BLT.HYD."},
        {"unit_id": 125, "name": "BLT.LUB"},
        {"unit_id": 126, "name": "BLT.SHELL"},
        {"unit_id": 1427, "name": "BOBCAT PAY LOADER"},
        {"unit_id": 136, "name": "BOD"},
        {"unit_id": 137, "name": "BOD PLANT"},
        {"unit_id": 138, "name": "BOF"},
        {"unit_id": 1465, "name": "BOF-APCS"},
        {"unit_id": 139, "name": "BOILER"},
        {"unit_id": 140, "name": "BOILER 1&2"},
        {"unit_id": 141, "name": "BOILER HOUSE"},
        {"unit_id": 142, "name": "BOILER PLANT"},
        {"unit_id": 143, "name": "BOILER-3&4"},
        {"unit_id": 144, "name": "BOILER-5&6"},
        {"unit_id": 145, "name": "BOILERS"},
        {"unit_id": 146, "name": "BOOSTERS"},
        {"unit_id": 147, "name": "BORING M/C"},
        {"unit_id": 148, "name": "BOX ANNEAL"},
        {"unit_id": 1524, "name": "BPTG"},
        {"unit_id": 149, "name": "BRAKE DRUM"},
        {"unit_id": 150, "name": "BREAST ROLL"},
        {"unit_id": 151, "name": "BRICK PLANT"},
        {"unit_id": 152, "name": "BRICK PRESS"},
        {"unit_id": 153, "name": "BRICKS"},
        {"unit_id": 154, "name": "BRIDDLE"},
        {"unit_id": 155, "name": "BU&ST LINE"},
        {"unit_id": 156, "name": "BUILD UP"},
        {"unit_id": 157, "name": "BUILDING"},
        {"unit_id": 158, "name": "BUNKERS"},
        {"unit_id": 1506, "name": "BUR CHOCK"},
        {"unit_id": 1434, "name": "BURNERS"},
        {"unit_id": 159, "name": "BUST"},
        {"unit_id": 160, "name": "C&J.W.PUMP"},
        {"unit_id": 161, "name": "C&JET WATER"},
        {"unit_id": 162, "name": "C&S STATION"},
        {"unit_id": 163, "name": "C.A.COMPRESS"},
        {"unit_id": 164, "name": "C.A.LINE"},
        {"unit_id": 165, "name": "C.A.SYSTEM"},
        {"unit_id": 166, "name": "C.ACID"},
        {"unit_id": 167, "name": "C.ACID PLANT"},
        {"unit_id": 169, "name": "C.AIR SUPPLY"},
        {"unit_id": 170, "name": "C.B.PIPING"},
        {"unit_id": 171, "name": "C.B.PLANT"},
        {"unit_id": 172, "name": "C.BAGGING"},
        {"unit_id": 173, "name": "C.C.S"},
        {"unit_id": 174, "name": "C.CAR"},
        {"unit_id": 175, "name": "C.COMPRESSOR"},
        {"unit_id": 176, "name": "C.CONVEYING"},
        {"unit_id": 177, "name": "C.DISPOSAL"},
        {"unit_id": 178, "name": "C.E.H SYSTEM"},
        {"unit_id": 179, "name": "C.E.HANDLING"},
        {"unit_id": 180, "name": "C.EQUIPMENT"},
        {"unit_id": 181, "name": "C.F.BRIDGE"},
        {"unit_id": 182, "name": "C.H&M.HOUSE"},
        {"unit_id": 183, "name": "C.H.PLANT"},
        {"unit_id": 184, "name": "C.H.SYSTEM"},
        {"unit_id": 185, "name": "C.HANDLING"},
        {"unit_id": 186, "name": "C.I&S.SHEAR"},
        {"unit_id": 187, "name": "C.M.IMPACT"},
        {"unit_id": 188, "name": "C.M.M/C"},
        {"unit_id": 189, "name": "C.M/C"},
        {"unit_id": 190, "name": "C.P.LEVELLER"},
        {"unit_id": 191, "name": "C.PUSHER"},
        {"unit_id": 192, "name": "C.S.M/C"},
        {"unit_id": 193, "name": "C.S.SCREEN"},
        {"unit_id": 194, "name": "C.S.SEPARATE"},
        {"unit_id": 195, "name": "C.S.STATION"},
        {"unit_id": 196, "name": "C.SCREENING"},
        {"unit_id": 1356, "name": "C.SYSTEM"},
        {"unit_id": 197, "name": "C.T.S"},
        {"unit_id": 198, "name": "C.T.SHEAR"},
        {"unit_id": 199, "name": "C.TOWER"},
        {"unit_id": 200, "name": "C.TRANSFER"},
        {"unit_id": 1371, "name": "C.W.HOPPER"},
        {"unit_id": 201, "name": "C.W.P.HOUSE"},
        {"unit_id": 202, "name": "C.W.PUMP"},
        {"unit_id": 203, "name": "C.W.SYSTEM"},
        {"unit_id": 204, "name": "C.W.T"},
        {"unit_id": 205, "name": "C.WATER"},
        {"unit_id": 206, "name": "CABLE DUCT"},
        {"unit_id": 1402, "name": "CABLE GALLERIES"},
        {"unit_id": 207, "name": "CABLE ROUTE"},
        {"unit_id": 208, "name": "CABLE TUNNEL"},
        {"unit_id": 209, "name": "CAL.PLANT"},
        {"unit_id": 210, "name": "CALOW M/C"},
        {"unit_id": 211, "name": "CAR"},
        {"unit_id": 212, "name": "CAR GCP"},
        {"unit_id": 213, "name": "CAR PUSHER"},
        {"unit_id": 214, "name": "CAR TRANSFER"},
        {"unit_id": 215, "name": "CARLITE"},
        {"unit_id": 216, "name": "CARLITE LINE"},
        {"unit_id": 217, "name": "CARS"},
        {"unit_id": 218, "name": "CARS2"},
        {"unit_id": 219, "name": "CAST HOUSE"},
        {"unit_id": 1428, "name": "CASTER"},
        {"unit_id": 1425, "name": "CASTER-II"},
        {"unit_id": 2, "name": "CASTER-III"},
        {"unit_id": 1374, "name": "CASTER-IV"},
        {"unit_id": 220, "name": "CASTING EQPT"},
        {"unit_id": 221, "name": "CCM-1"},
        {"unit_id": 222, "name": "CCM-2"},
        {"unit_id": 1406, "name": "CCM-3"},
        {"unit_id": 1357, "name": "CCP"},
        {"unit_id": 223, "name": "CCS"},
        {"unit_id": 224, "name": "CCS R.MILL"},
        {"unit_id": 1375, "name": "CDCP"},
        {"unit_id": 1407, "name": "CDI"},
        {"unit_id": 225, "name": "CED"},
        {"unit_id": 226, "name": "CEH SYSTEM"},
        {"unit_id": 227, "name": "CENTER DRIVE"},
        {"unit_id": 228, "name": "CENTRAL LAB"},
        {"unit_id": 1367, "name": "CERAMICS"},
        {"unit_id": 229, "name": "CH.WATER TNT"},
        {"unit_id": 230, "name": "CHARGING CAR"},
        {"unit_id": 1366, "name": "CHEMICAL"},
        {"unit_id": 231, "name": "CHILL WATER"},
        {"unit_id": 232, "name": "CHOCK"},
        {"unit_id": 233, "name": "CHP"},
        {"unit_id": 234, "name": "CHUTES"},
        {"unit_id": 235, "name": "CIOL BOX"},
        {"unit_id": 236, "name": "CIVIL"},
        {"unit_id": 237, "name": "CKT BREAKER"},
        {"unit_id": 1426, "name": "CLARIFIER"},
        {"unit_id": 238, "name": "CLEANING SEC"},
        {"unit_id": 239, "name": "CMM-1"},
        {"unit_id": 1527, "name": "CNC MACHINE"},
        {"unit_id": 240, "name": "CNSTRUCTION"},
        {"unit_id": 241, "name": "CNVEYOR"},
        {"unit_id": 242, "name": "COAL FEEDER"},
        {"unit_id": 243, "name": "COAL HAMMER"},
        {"unit_id": 244, "name": "COAL HANDLNG"},
        {"unit_id": 245, "name": "COAL MILLS"},
        {"unit_id": 246, "name": "COAL SCREEN"},
        {"unit_id": 247, "name": "COALFEER"},
        {"unit_id": 248, "name": "COALHANDLNG."},
        {"unit_id": 1535, "name": "COARSE CONDENSATION PLANT"},
        {"unit_id": 249, "name": "COATING RIG"},
        {"unit_id": 1511, "name": "COBBLE CATCHER"},
        {"unit_id": 1504, "name": "COBBLER PUSHER"},
        {"unit_id": 250, "name": "COIL BOX"},
        {"unit_id": 251, "name": "COIL CONV."},
        {"unit_id": 252, "name": "COIL CONVEY"},
        {"unit_id": 254, "name": "COIL PREPARE"},
        {"unit_id": 1512, "name": "COIL STRIPPER CAR"},
        {"unit_id": 255, "name": "COIL TRANS."},
        {"unit_id": 253, "name": "COIL YARD"},
        {"unit_id": 256, "name": "COILER"},
        {"unit_id": 257, "name": "COILER-4&5"},
        {"unit_id": 258, "name": "COILER-5"},
        {"unit_id": 259, "name": "COILERS"},
        {"unit_id": 260, "name": "COILERS-4&5"},
        {"unit_id": 261, "name": "COKE BREEZE"},
        {"unit_id": 262, "name": "COKE CRUSHER"},
        {"unit_id": 263, "name": "COKE FEEDING"},
        {"unit_id": 264, "name": "COKE HANDLG"},
        {"unit_id": 1469, "name": "COKE OVENS"},
        {"unit_id": 265, "name": "COKE SCREEN"},
        {"unit_id": 266, "name": "COLD BOX"},
        {"unit_id": 267, "name": "COLD SAW"},
        {"unit_id": 268, "name": "COLD SCREEN"},
        {"unit_id": 269, "name": "COMB.SYSTEM"},
        {"unit_id": 270, "name": "COMBUSTION"},
        {"unit_id": 271, "name": "COMMUNICATN"},
        {"unit_id": 272, "name": "COMP HOUSE"},
        {"unit_id": 273, "name": "COMPRESS AIR"},
        {"unit_id": 274, "name": "COMPRESS STN"},
        {"unit_id": 275, "name": "COMPRESSOR"},
        {"unit_id": 276, "name": "CON.EQPT"},
        {"unit_id": 277, "name": "CONCRETE"},
        {"unit_id": 278, "name": "CONDENSATE"},
        {"unit_id": 279, "name": "CONE CRUSHER"},
        {"unit_id": 280, "name": "CONEYOR"},
        {"unit_id": 281, "name": "CONST EQPT"},
        {"unit_id": 282, "name": "CONSTRUCTION"},
        {"unit_id": 283, "name": "CONTROL ROOM"},
        {"unit_id": 284, "name": "CONV EQPT"},
        {"unit_id": 285, "name": "CONV.SYSTEM"},
        {"unit_id": 1531, "name": "CONVERTER-1&2"},
        {"unit_id": 1439, "name": "CONVERTER-3"},
        {"unit_id": 286, "name": "CONVERTOR"},
        {"unit_id": 287, "name": "CONVEYOR"},
        {"unit_id": 288, "name": "COOL STACKS"},
        {"unit_id": 289, "name": "COOL TOWER"},
        {"unit_id": 290, "name": "COOL.ARRGT"},
        {"unit_id": 291, "name": "COOL.SYSTEM"},
        {"unit_id": 292, "name": "COOLER"},
        {"unit_id": 293, "name": "COOLING"},
        {"unit_id": 294, "name": "COOLING BED"},
        {"unit_id": 1380, "name": "COOLING BED-1"},
        {"unit_id": 1381, "name": "COOLING BED-2"},
        {"unit_id": 295, "name": "COOLING BELT"},
        {"unit_id": 296, "name": "COOLING HOOD"},
        {"unit_id": 297, "name": "COPY MILLING"},
        {"unit_id": 298, "name": "CPL"},
        {"unit_id": 299, "name": "CR 1&2"},
        {"unit_id": 300, "name": "CR&SP 1/2"},
        {"unit_id": 302, "name": "CR-1"},
        {"unit_id": 303, "name": "CR-1&2"},
        {"unit_id": 304, "name": "CR-1/2"},
        {"unit_id": 305, "name": "CR-2"},
        {"unit_id": 301, "name": "CR.#235"},
        {"unit_id": 1358, "name": "CRANE"},
        {"unit_id": 306, "name": "CRANE HOIST"},
        {"unit_id": 307, "name": "CRM"},
        {"unit_id": 308, "name": "CRM BOILER"},
        {"unit_id": 309, "name": "CROP DISPOSE"},
        {"unit_id": 310, "name": "CROP SHEAR"},
        {"unit_id": 311, "name": "CROSS SEAM"},
        {"unit_id": 312, "name": "CRS"},
        {"unit_id": 313, "name": "CRUD BENZOL"},
        {"unit_id": 314, "name": "CRUDE BENTOL"},
        {"unit_id": 315, "name": "CRUSG&SCREEN"},
        {"unit_id": 316, "name": "CRUSHER"},
        {"unit_id": 317, "name": "CRUSHING"},
        {"unit_id": 319, "name": "CTS"},
        {"unit_id": 320, "name": "CTS GEAR BOX"},
        {"unit_id": 321, "name": "CUPOLA"},
        {"unit_id": 322, "name": "CUPOLA-4"},
        {"unit_id": 323, "name": "CUPOLAS"},
        {"unit_id": 324, "name": "CURSHING"},
        {"unit_id": 1476, "name": "CUT TO LENGTH"},
        {"unit_id": 325, "name": "CUTT OFF M/C"},
        {"unit_id": 1533, "name": "CUTTER M/C"},
        {"unit_id": 326, "name": "CW RECYLING"},
        {"unit_id": 318, "name": "CWPH"},
        {"unit_id": 327, "name": "CWT"},
        {"unit_id": 328, "name": "CYCLOMETIC"},
        {"unit_id": 329, "name": "D&A SECTION"},
        {"unit_id": 330, "name": "D.BAR SYSTEM"},
        {"unit_id": 331, "name": "D.C.PUMP"},
        {"unit_id": 332, "name": "D.C.SYSTEM"},
        {"unit_id": 333, "name": "D.COOLER"},
        {"unit_id": 334, "name": "D.E.SYSTEM"},
        {"unit_id": 335, "name": "D.G.M/C"},
        {"unit_id": 336, "name": "D.MIXERS"},
        {"unit_id": 337, "name": "D.PLANT"},
        {"unit_id": 338, "name": "D.S.A.PLANT"},
        {"unit_id": 339, "name": "D.S.ACID"},
        {"unit_id": 340, "name": "D.S.P"},
        {"unit_id": 1480, "name": "D.S.STATION"},
        {"unit_id": 341, "name": "D.SHEAR"},
        {"unit_id": 342, "name": "D.SULPHURIC"},
        {"unit_id": 343, "name": "D.SYSTEM"},
        {"unit_id": 344, "name": "D.W&H.TANK"},
        {"unit_id": 345, "name": "D.W.STATION"},
        {"unit_id": 346, "name": "D.WATER"},
        {"unit_id": 347, "name": "DCDA PLANT"},
        {"unit_id": 1393, "name": "DCW PUMP HOUSES & PIPE LINES"},
        {"unit_id": 1478, "name": "DECANTER BTL"},
        {"unit_id": 348, "name": "DECARB"},
        {"unit_id": 349, "name": "DECARB LINE"},
        {"unit_id": 350, "name": "DECARB MILL"},
        {"unit_id": 351, "name": "DECARB&TA"},
        {"unit_id": 352, "name": "DEDUST PLANT"},
        {"unit_id": 353, "name": "DEDUSTING"},
        {"unit_id": 1494, "name": "DEGREASING"},
        {"unit_id": 1518, "name": "DELIVERY CAR"},
        {"unit_id": 354, "name": "DEPHENOLISE"},
        {"unit_id": 355, "name": "DESCALING"},
        {"unit_id": 1391, "name": "DESCALING SYSTEM"},
        {"unit_id": 356, "name": "DESIGN"},
        {"unit_id": 357, "name": "DESLAGING"},
        {"unit_id": 358, "name": "DEVIDE SHEAR"},
        {"unit_id": 359, "name": "DINK WATER"},
        {"unit_id": 360, "name": "DISCAL PUMP"},
        {"unit_id": 361, "name": "DISTILLATION"},
        {"unit_id": 362, "name": "DISTRIBUTION"},
        {"unit_id": 363, "name": "DIVIDING"},
        {"unit_id": 1385, "name": "DIVIDING SHEAR"},
        {"unit_id": 364, "name": "DOLO ROTARY"},
        {"unit_id": 1529, "name": "DOUBLE ROLL CRUSHER"},
        {"unit_id": 1384, "name": "DOUBLE SIDE TRIMMING SHEAR"},
        {"unit_id": 365, "name": "DOWN COILER"},
        {"unit_id": 366, "name": "DRILLING M/C"},
        {"unit_id": 367, "name": "DRIVE SHEAR"},
        {"unit_id": 368, "name": "DRY SECTION"},
        {"unit_id": 369, "name": "DRY SULPHUR"},
        {"unit_id": 370, "name": "DRYING FCE"},
        {"unit_id": 371, "name": "DRYING OVEN"},
        {"unit_id": 372, "name": "DRYING SEC."},
        {"unit_id": 1496, "name": "DS KNIFE SLEDGE"},
        {"unit_id": 373, "name": "DSP"},
        {"unit_id": 374, "name": "DUMMY BAR"},
        {"unit_id": 375, "name": "DUST CATCHER"},
        {"unit_id": 376, "name": "DUST COLLECT"},
        {"unit_id": 377, "name": "DW & HL TANK"},
        {"unit_id": 378, "name": "E.ARC FCE."},
        {"unit_id": 379, "name": "E.B.M/C"},
        {"unit_id": 380, "name": "E.S.P"},
        {"unit_id": 381, "name": "E.SHEAR M/C"},
        {"unit_id": 1479, "name": "E.T. TROLLEY"},
        {"unit_id": 382, "name": "E.TRIMMING"},
        {"unit_id": 1398, "name": "ECR-1"},
        {"unit_id": 1399, "name": "ECR-2"},
        {"unit_id": 1400, "name": "ECR-3"},
        {"unit_id": 383, "name": "EDDY CURRENT"},
        {"unit_id": 384, "name": "EDGE TRIMMER"},
        {"unit_id": 385, "name": "EDP"},
        {"unit_id": 386, "name": "ELECT HOIST"},
        {"unit_id": 387, "name": "ELECTRICAL"},
        {"unit_id": 388, "name": "ELECTRO ROLL"},
        {"unit_id": 389, "name": "ELEVATOR"},
        {"unit_id": 390, "name": "EM-7"},
        {"unit_id": 391, "name": "ENT.SECTION"},
        {"unit_id": 392, "name": "ENTRY CONV."},
        {"unit_id": 393, "name": "ENTRY GUIDE"},
        {"unit_id": 394, "name": "EQIPMENT"},
        {"unit_id": 395, "name": "EQPT"},
        {"unit_id": 396, "name": "EQPT.LAYOUT"},
        {"unit_id": 397, "name": "EQUAL.PIPE"},
        {"unit_id": 398, "name": "EQUALIZING"},
        {"unit_id": 399, "name": "EQUIPMENT"},
        {"unit_id": 400, "name": "ERECTION"},
        {"unit_id": 401, "name": "ERS"},
        {"unit_id": 402, "name": "ESP"},
        {"unit_id": 403, "name": "ESTP"},
        {"unit_id": 404, "name": "ETL"},
        {"unit_id": 405, "name": "ETP"},
        {"unit_id": 406, "name": "ETS"},
        {"unit_id": 407, "name": "ETSL"},
        {"unit_id": 408, "name": "EW-9&10"},
        {"unit_id": 409, "name": "EXHAUSTER"},
        {"unit_id": 410, "name": "EXPN TURBINE"},
        {"unit_id": 411, "name": "F.A.H.SYSTEM"},
        {"unit_id": 412, "name": "F.A.HANDLING"},
        {"unit_id": 413, "name": "F.B.C.BOILER"},
        {"unit_id": 414, "name": "F.C.& SCREEN"},
        {"unit_id": 415, "name": "F.C.EQPT"},
        {"unit_id": 416, "name": "F.C.M/C"},
        {"unit_id": 417, "name": "F.C.M/C-2"},
        {"unit_id": 418, "name": "F.C.MECHINE"},
        {"unit_id": 419, "name": "F.C.OFF M/C"},
        {"unit_id": 420, "name": "F.C.P.HOUSE"},
        {"unit_id": 421, "name": "F.C.SYSTEM"},
        {"unit_id": 422, "name": "F.C.TOWER"},
        {"unit_id": 423, "name": "F.COKE TOWER"},
        {"unit_id": 424, "name": "F.CRUSHING"},
        {"unit_id": 425, "name": "F.CUTTING"},
        {"unit_id": 426, "name": "F.D.FAN"},
        {"unit_id": 427, "name": "F.E.SYSTEM"},
        {"unit_id": 428, "name": "F.F&MOUNTING"},
        {"unit_id": 429, "name": "F.F.COOLER"},
        {"unit_id": 430, "name": "F.F.EQPT"},
        {"unit_id": 431, "name": "F.F.SYSTEM"},
        {"unit_id": 432, "name": "F.FEEDER"},
        {"unit_id": 433, "name": "F.H.EQPT"},
        {"unit_id": 434, "name": "F.H.SYSTEM"},
        {"unit_id": 435, "name": "F.LINE"},
        {"unit_id": 436, "name": "F.MECHINARY"},
        {"unit_id": 437, "name": "F.O.H.SYSTEM"},
        {"unit_id": 438, "name": "F.P.SYSTEM"},
        {"unit_id": 439, "name": "F.PLANT"},
        {"unit_id": 440, "name": "F.R.SUSPENS"},
        {"unit_id": 441, "name": "F.STAND"},
        {"unit_id": 442, "name": "FABN.SHOP"},
        {"unit_id": 443, "name": "FABRICATION"},
        {"unit_id": 444, "name": "FATLING SEC"},
        {"unit_id": 445, "name": "FCE C.EQPT"},
        {"unit_id": 446, "name": "FCE CHARGING"},
        {"unit_id": 447, "name": "FCE COOLING"},
        {"unit_id": 448, "name": "FCE FITTING"},
        {"unit_id": 449, "name": "FCE MOUNTING"},
        {"unit_id": 450, "name": "FCE SHELL"},
        {"unit_id": 451, "name": "FCE TOP"},
        {"unit_id": 452, "name": "FCE TOP EQPT"},
        {"unit_id": 459, "name": "FCE-5&6"},
        {"unit_id": 453, "name": "FCE. F&M"},
        {"unit_id": 454, "name": "FCE. SHELL"},
        {"unit_id": 455, "name": "FCE.COOLING"},
        {"unit_id": 456, "name": "FCE.EQPT"},
        {"unit_id": 457, "name": "FCE.FITTING"},
        {"unit_id": 458, "name": "FCE.SHELL"},
        {"unit_id": 460, "name": "FEED HEATING"},
        {"unit_id": 461, "name": "FEED PUMP"},
        {"unit_id": 462, "name": "FEED WATER"},
        {"unit_id": 463, "name": "FETTLING SEC"},
        {"unit_id": 464, "name": "FILTER"},
        {"unit_id": 465, "name": "FINAL COOLER"},
        {"unit_id": 466, "name": "FINISH LINE"},
        {"unit_id": 467, "name": "FINISH MILL"},
        {"unit_id": 468, "name": "FINISH STAND"},
        {"unit_id": 469, "name": "FINISHING"},
        {"unit_id": 1389, "name": "FINISHING SCALE BREAKER"},
        {"unit_id": 1474, "name": "FIRE ALARM SYSTEM"},
        {"unit_id": 1359, "name": "FIRE FIGHTNG"},
        {"unit_id": 470, "name": "FIRE HYDRANT"},
        {"unit_id": 471, "name": "FIRE PROTECT"},
        {"unit_id": 472, "name": "FIRE SERVICE"},
        {"unit_id": 473, "name": "FIRE STATION"},
        {"unit_id": 474, "name": "FIRE SYSTEM"},
        {"unit_id": 475, "name": "FIRE TENDER"},
        {"unit_id": 476, "name": "FITTING"},
        {"unit_id": 477, "name": "FITTING SEC"},
        {"unit_id": 478, "name": "FLAME C.M/C"},
        {"unit_id": 479, "name": "FLAME CUT"},
        {"unit_id": 1416, "name": "FLARE STACK"},
        {"unit_id": 1468, "name": "FLIP FLOW SCREEN"},
        {"unit_id": 480, "name": "FLUX CRUSH"},
        {"unit_id": 481, "name": "FLUX HANDLG"},
        {"unit_id": 1418, "name": "FLUX SCREENING"},
        {"unit_id": 482, "name": "FLUX&FUEL"},
        {"unit_id": 483, "name": "FLY CUTTER"},
        {"unit_id": 484, "name": "FLYING SHEAR"},
        {"unit_id": 1508, "name": "FM BUR CHANGING DEVICE"},
        {"unit_id": 1507, "name": "FM GUIDE"},
        {"unit_id": 1509, "name": "FM WR CHANGING DEVICE"},
        {"unit_id": 485, "name": "FORING STAND"},
        {"unit_id": 486, "name": "FORMER STAND"},
        {"unit_id": 487, "name": "FORMING"},
        {"unit_id": 488, "name": "FORMING STD"},
        {"unit_id": 489, "name": "FOUNDATION"},
        {"unit_id": 490, "name": "FOUNDRIES"},
        {"unit_id": 491, "name": "FP"},
        {"unit_id": 492, "name": "FRACTINATION"},
        {"unit_id": 493, "name": "FUEL CRUSHNG"},
        {"unit_id": 1442, "name": "FUEL SYSTEM"},
        {"unit_id": 1523, "name": "FUME EXHAUST HOOD"},
        {"unit_id": 494, "name": "FUNACE"},
        {"unit_id": 495, "name": "FUONDATION"},
        {"unit_id": 496, "name": "FURNACE"},
        {"unit_id": 497, "name": "FURNACE F&M"},
        {"unit_id": 1452, "name": "FURNACE PROPER"},
        {"unit_id": 498, "name": "FURNACE SHEL"},
        {"unit_id": 499, "name": "FURNACE-5&6"},
        {"unit_id": 500, "name": "FURNACES"},
        {"unit_id": 501, "name": "G.ASSEMBLY"},
        {"unit_id": 502, "name": "G.B.EXHAUST"},
        {"unit_id": 503, "name": "G.C&P.COOLER"},
        {"unit_id": 504, "name": "G.C.COOLER"},
        {"unit_id": 505, "name": "G.C.P.COOLER"},
        {"unit_id": 506, "name": "G.CAR"},
        {"unit_id": 507, "name": "G.FACILITY"},
        {"unit_id": 508, "name": "G.P.LINE"},
        {"unit_id": 509, "name": "G.ROLLER"},
        {"unit_id": 510, "name": "GAL LINE"},
        {"unit_id": 511, "name": "GAL LINE-1"},
        {"unit_id": 512, "name": "GAL LINE-2"},
        {"unit_id": 514, "name": "GAL-1"},
        {"unit_id": 513, "name": "GAL.LINE"},
        {"unit_id": 515, "name": "GALVANISING"},
        {"unit_id": 516, "name": "GAS BOOSTER"},
        {"unit_id": 517, "name": "GAS CONDEN"},
        {"unit_id": 518, "name": "GAS CONDTN."},
        {"unit_id": 1461, "name": "GAS DISTRIBUTION PLANT"},
        {"unit_id": 519, "name": "GAS EXHAUST"},
        {"unit_id": 520, "name": "GAS GENERAL"},
        {"unit_id": 521, "name": "GAS HOLDER"},
        {"unit_id": 522, "name": "GAS LINE"},
        {"unit_id": 523, "name": "GAS MAIN"},
        {"unit_id": 524, "name": "GAS MAINS"},
        {"unit_id": 525, "name": "GAS PIPELINE"},
        {"unit_id": 526, "name": "GCP"},
        {"unit_id": 527, "name": "GCP CAR"},
        {"unit_id": 528, "name": "GCP/GRP"},
        {"unit_id": 529, "name": "GENERAL"},
        {"unit_id": 530, "name": "GENERAL SITE"},
        {"unit_id": 531, "name": "GENL LAYOUT"},
        {"unit_id": 532, "name": "GENL.ARRGT"},
        {"unit_id": 534, "name": "GL-2"},
        {"unit_id": 533, "name": "GLAND PACKING"},
        {"unit_id": 535, "name": "GRAIN HEATER"},
        {"unit_id": 536, "name": "GRANULATION"},
        {"unit_id": 537, "name": "GREASE & HYD"},
        {"unit_id": 538, "name": "GREASING"},
        {"unit_id": 539, "name": "GRIND MILL"},
        {"unit_id": 540, "name": "GRINDING"},
        {"unit_id": 541, "name": "GRINDING M/C"},
        {"unit_id": 542, "name": "GUIDE CAR"},
        {"unit_id": 543, "name": "GUY DEVICE"},
        {"unit_id": 544, "name": "H.A.LINE"},
        {"unit_id": 545, "name": "H.ANNEALING"},
        {"unit_id": 546, "name": "H.ARRGT."},
        {"unit_id": 547, "name": "H.B.M/C"},
        {"unit_id": 549, "name": "H.B.STOVES"},
        {"unit_id": 550, "name": "H.BORING M/C"},
        {"unit_id": 551, "name": "H.C.SHEAR"},
        {"unit_id": 552, "name": "H.D.STATION"},
        {"unit_id": 553, "name": "H.F.WELD.M/C"},
        {"unit_id": 554, "name": "H.F.WELDING"},
        {"unit_id": 555, "name": "H.FACILITY"},
        {"unit_id": 556, "name": "H.L.R.SHOP"},
        {"unit_id": 557, "name": "H.L.TANK"},
        {"unit_id": 558, "name": "H.P.LEVELLER"},
        {"unit_id": 559, "name": "H.P.PLANT"},
        {"unit_id": 560, "name": "H.P.PUMP"},
        {"unit_id": 561, "name": "H.R.MILL"},
        {"unit_id": 562, "name": "H.R.PLANT"},
        {"unit_id": 563, "name": "H.R.STAND"},
        {"unit_id": 564, "name": "H.REFINING"},
        {"unit_id": 565, "name": "H.S WITH C.D"},
        {"unit_id": 566, "name": "H.S.M/C"},
        {"unit_id": 567, "name": "H.S.SCREEN"},
        {"unit_id": 568, "name": "H.VEHICLE"},
        {"unit_id": 569, "name": "HALDEN SHEAR"},
        {"unit_id": 1453, "name": "HAMMER CRUSHER"},
        {"unit_id": 570, "name": "HAMMER MILL"},
        {"unit_id": 571, "name": "HANDLG ARRGT"},
        {"unit_id": 573, "name": "HANDLING"},
        {"unit_id": 572, "name": "HANDLING EQUIPMENT"},
        {"unit_id": 1501, "name": "HEAT HOLDING"},
        {"unit_id": 574, "name": "HEAT TREAT"},
        {"unit_id": 575, "name": "HEATING"},
        {"unit_id": 1396, "name": "HEAVY PLATE AREA & FLAME CUTTING"},
        {"unit_id": 576, "name": "HF WELDER"},
        {"unit_id": 1445, "name": "HIGH MAST"},
        {"unit_id": 577, "name": "HIGHLINES"},
        {"unit_id": 578, "name": "HM CAR"},
        {"unit_id": 579, "name": "HMT.LATHE"},
        {"unit_id": 1435, "name": "HOIST"},
        {"unit_id": 580, "name": "HOISTING M/C"},
        {"unit_id": 581, "name": "HOOD ANNEAL"},
        {"unit_id": 582, "name": "HOOD ANNEALG"},
        {"unit_id": 583, "name": "HOPPERS"},
        {"unit_id": 584, "name": "HOT BLAST"},
        {"unit_id": 585, "name": "HOT FLUE"},
        {"unit_id": 586, "name": "HOT LEVELLER"},
        {"unit_id": 587, "name": "HOT MILLS"},
        {"unit_id": 548, "name": "HOT SCARFING"},
        {"unit_id": 588, "name": "HOT SCREEN"},
        {"unit_id": 589, "name": "HSM"},
        {"unit_id": 590, "name": "HYD & LUB"},
        {"unit_id": 591, "name": "HYD PRESS"},
        {"unit_id": 592, "name": "HYD REFINING"},
        {"unit_id": 593, "name": "HYD SHEAR"},
        {"unit_id": 594, "name": "HYD TESTER"},
        {"unit_id": 595, "name": "HYD TESTING"},
        {"unit_id": 596, "name": "HYD.PRESS"},
        {"unit_id": 597, "name": "HYD.REFINE"},
        {"unit_id": 598, "name": "HYD.SHEAR"},
        {"unit_id": 599, "name": "HYD.SL.M/C"},
        {"unit_id": 600, "name": "HYD.TEST M/C"},
        {"unit_id": 601, "name": "HYD.TESTING"},
        {"unit_id": 1521, "name": "HYDRAULIC SCALE BREAKER"},
        {"unit_id": 602, "name": "HYDRAULICS"},
        {"unit_id": 603, "name": "HYDRO BLAST"},
        {"unit_id": 604, "name": "HYDRO REFINE"},
        {"unit_id": 605, "name": "HYDRO SHEAR"},
        {"unit_id": 606, "name": "HYDRO TESTER"},
        {"unit_id": 607, "name": "HYRAULICS"},
        {"unit_id": 608, "name": "I.B.R.TABLE"},
        {"unit_id": 609, "name": "I.C.PLANT"},
        {"unit_id": 610, "name": "I.COOLING"},
        {"unit_id": 1421, "name": "I.D.FAN"},
        {"unit_id": 611, "name": "I.FURNACE"},
        {"unit_id": 612, "name": "I.H.CRUSHER"},
        {"unit_id": 613, "name": "I.O.C.STN"},
        {"unit_id": 1420, "name": "I.P.T.F"},
        {"unit_id": 614, "name": "I.R.TABLE"},
        {"unit_id": 615, "name": "I.S.B.STR"},
        {"unit_id": 616, "name": "I.S.DEVICE"},
        {"unit_id": 617, "name": "I.S.HOIST"},
        {"unit_id": 618, "name": "I.S.STR"},
        {"unit_id": 619, "name": "I.TRIMMING"},
        {"unit_id": 1392, "name": "ICW PUMP HOUSES & PIPE LINES"},
        {"unit_id": 620, "name": "IGH"},
        {"unit_id": 621, "name": "IGN.FURNACE"},
        {"unit_id": 622, "name": "IGNITION FCE"},
        {"unit_id": 623, "name": "IMPACT MILL"},
        {"unit_id": 1431, "name": "IMPACT TESTING M/C"},
        {"unit_id": 624, "name": "INDICATOR"},
        {"unit_id": 625, "name": "INDUCTN FCE"},
        {"unit_id": 626, "name": "ING.FURNACE"},
        {"unit_id": 627, "name": "INGITION FCE"},
        {"unit_id": 628, "name": "INGOT BAY"},
        {"unit_id": 629, "name": "INGOT BOGGY"},
        {"unit_id": 630, "name": "INGOT CAR"},
        {"unit_id": 631, "name": "INGOT FCE"},
        {"unit_id": 632, "name": "INGOT GUGGY"},
        {"unit_id": 633, "name": "INGOT MOULD"},
        {"unit_id": 634, "name": "INSP.&FINISH"},
        {"unit_id": 635, "name": "INSPECTION"},
        {"unit_id": 1382, "name": "INSPECTION BED"},
        {"unit_id": 636, "name": "INSPN&FINISH"},
        {"unit_id": 1475, "name": "INSTRON UTM 1000 KN"},
        {"unit_id": 637, "name": "INSTRUMENT"},
        {"unit_id": 638, "name": "INT.COOLING"},
        {"unit_id": 639, "name": "INTAKE WELL"},
        {"unit_id": 640, "name": "IOC STATION"},
        {"unit_id": 641, "name": "IOS STATION"},
        {"unit_id": 642, "name": "IRON&STEEL"},
        {"unit_id": 643, "name": "ISPAT PRESS"},
        {"unit_id": 644, "name": "J.HOUSE"},
        {"unit_id": 645, "name": "JET COATING"},
        {"unit_id": 646, "name": "JH HOUSE"},
        {"unit_id": 647, "name": "JN.HOUSE"},
        {"unit_id": 648, "name": "K.C.SYSTEM"},
        {"unit_id": 649, "name": "K.D.SYSTEM"},
        {"unit_id": 650, "name": "K.S-4&5"},
        {"unit_id": 651, "name": "KALTA"},
        {"unit_id": 1437, "name": "KILN 5 & 6"},
        {"unit_id": 652, "name": "KILN COOLER"},
        {"unit_id": 653, "name": "KILN FEED"},
        {"unit_id": 654, "name": "KILN SHAFT"},
        {"unit_id": 655, "name": "KILN&COOLER"},
        {"unit_id": 656, "name": "KILN-1,2,3"},
        {"unit_id": 657, "name": "KILN-4"},
        {"unit_id": 658, "name": "KILN-5"},
        {"unit_id": 659, "name": "KILN-8"},
        {"unit_id": 660, "name": "KILNS"},
        {"unit_id": 661, "name": "KNOCK CRANE"},
        {"unit_id": 662, "name": "L. & TUNDISH"},
        {"unit_id": 663, "name": "L.B.PLATES"},
        {"unit_id": 664, "name": "L.C SYSTEM"},
        {"unit_id": 665, "name": "L.D.40T"},
        {"unit_id": 666, "name": "L.D.CONVEYOR"},
        {"unit_id": 667, "name": "L.D.CONVRTER"},
        {"unit_id": 668, "name": "L.D.RELINING"},
        {"unit_id": 669, "name": "L.D.STAND"},
        {"unit_id": 670, "name": "L.D.VESSEL"},
        {"unit_id": 673, "name": "L.M.B.PLATE"},
        {"unit_id": 674, "name": "L.M.PLANT"},
        {"unit_id": 675, "name": "L.N.SYSTEM"},
        {"unit_id": 676, "name": "L.O.C.PUMP"},
        {"unit_id": 677, "name": "L.O2.PUMP"},
        {"unit_id": 678, "name": "L.OXYGEN"},
        {"unit_id": 679, "name": "L.R.S"},
        {"unit_id": 680, "name": "L.R.SHOP"},
        {"unit_id": 681, "name": "L.ROLLER"},
        {"unit_id": 682, "name": "L.S.CRUSHER"},
        {"unit_id": 683, "name": "L.S.CRUSHING"},
        {"unit_id": 684, "name": "L.S.K.4"},
        {"unit_id": 685, "name": "L.S.KILN-2"},
        {"unit_id": 686, "name": "L.S.KILN-5"},
        {"unit_id": 687, "name": "L.SHAFT KILN"},
        {"unit_id": 688, "name": "LAB EQPT."},
        {"unit_id": 689, "name": "LADDLE"},
        {"unit_id": 690, "name": "LADDLE DRYNG"},
        {"unit_id": 691, "name": "LADER"},
        {"unit_id": 692, "name": "LADLE"},
        {"unit_id": 1360, "name": "LADLE CAR"},
        {"unit_id": 693, "name": "LADLE DRIERS"},
        {"unit_id": 694, "name": "LADLE REPAIR"},
        {"unit_id": 695, "name": "LADLE STAND"},
        {"unit_id": 696, "name": "LADLE TURRET"},
        {"unit_id": 697, "name": "LADLES"},
        {"unit_id": 698, "name": "LANCE"},
        {"unit_id": 699, "name": "LANCE EQPT."},
        {"unit_id": 700, "name": "LATHE M/C"},
        {"unit_id": 701, "name": "LAYOUT"},
        {"unit_id": 702, "name": "LAYOUT EQPT"},
        {"unit_id": 1408, "name": "LBDS"},
        {"unit_id": 1448, "name": "LBSS-1"},
        {"unit_id": 703, "name": "LD CONVERTER"},
        {"unit_id": 704, "name": "LDS STATION"},
        {"unit_id": 705, "name": "LEVELLER"},
        {"unit_id": 706, "name": "LEVELLER-1"},
        {"unit_id": 1493, "name": "LEVELLING ROLL CASSETTE"},
        {"unit_id": 707, "name": "LHF"},
        {"unit_id": 708, "name": "LHS"},
        {"unit_id": 709, "name": "LIFTS"},
        {"unit_id": 710, "name": "LIGHTING"},
        {"unit_id": 711, "name": "LIME CRUSHER"},
        {"unit_id": 712, "name": "LIME KILNS"},
        {"unit_id": 713, "name": "LIME KLINE"},
        {"unit_id": 1413, "name": "LIME SCREENING UNIT"},
        {"unit_id": 714, "name": "LIME SHAHT"},
        {"unit_id": 1429, "name": "LIME SIZING"},
        {"unit_id": 1412, "name": "LIME SPLASHER"},
        {"unit_id": 715, "name": "LIME.S.KILN"},
        {"unit_id": 1530, "name": "LINER"},
        {"unit_id": 716, "name": "LIQUID STORE"},
        {"unit_id": 717, "name": "LOADING BIN"},
        {"unit_id": 718, "name": "LOCO MAINT"},
        {"unit_id": 719, "name": "LOCO SHED"},
        {"unit_id": 720, "name": "LOCOS"},
        {"unit_id": 721, "name": "LRS"},
        {"unit_id": 1443, "name": "LSU"},
        {"unit_id": 722, "name": "LUB.SYSTEM"},
        {"unit_id": 723, "name": "LUBRICATION"},
        {"unit_id": 724, "name": "M&B DRUM"},
        {"unit_id": 743, "name": "M-11"},
        {"unit_id": 744, "name": "M-12"},
        {"unit_id": 725, "name": "M.H.B.I.MINE"},
        {"unit_id": 726, "name": "M.H.I.O.MINE"},
        {"unit_id": 728, "name": "M.HOUSE"},
        {"unit_id": 729, "name": "M.P BOILER"},
        {"unit_id": 730, "name": "M.P.B-3"},
        {"unit_id": 731, "name": "M.P.BAY"},
        {"unit_id": 732, "name": "M.P.BOILER"},
        {"unit_id": 733, "name": "M.P.BOILER-3"},
        {"unit_id": 734, "name": "M.S.LINE"},
        {"unit_id": 735, "name": "M.T.HOUSE"},
        {"unit_id": 736, "name": "M.TEST HOUSE"},
        {"unit_id": 737, "name": "M.TRIPPER"},
        {"unit_id": 738, "name": "M.YARD"},
        {"unit_id": 739, "name": "M/C COMPONET"},
        {"unit_id": 740, "name": "M/C EQPT"},
        {"unit_id": 741, "name": "M/C TOOLS"},
        {"unit_id": 742, "name": "M/C-WG6,7,8"},
        {"unit_id": 1447, "name": "M1"},
        {"unit_id": 745, "name": "M2"},
        {"unit_id": 1483, "name": "M2.1"},
        {"unit_id": 746, "name": "M28"},
        {"unit_id": 747, "name": "MACHINARIES"},
        {"unit_id": 748, "name": "MACHINE TOOL"},
        {"unit_id": 749, "name": "MAGNETIC LAB"},
        {"unit_id": 750, "name": "MAIN BLOWER"},
        {"unit_id": 751, "name": "MAIN EQPT"},
        {"unit_id": 752, "name": "MAIN M/C"},
        {"unit_id": 753, "name": "MAIN M/C M2"},
        {"unit_id": 754, "name": "MAIN M/C-2"},
        {"unit_id": 755, "name": "MAIN MILL"},
        {"unit_id": 756, "name": "MAINT EQPT"},
        {"unit_id": 757, "name": "MANDIRA DAM"},
        {"unit_id": 758, "name": "MANUPULATOR"},
        {"unit_id": 1387, "name": "MARKING & PUNCHING M/C"},
        {"unit_id": 1379, "name": "MARKING M/C-1"},
        {"unit_id": 727, "name": "MATERIAL HANDLING"},
        {"unit_id": 759, "name": "MAYUR"},
        {"unit_id": 1386, "name": "MEASURING ROLL"},
        {"unit_id": 760, "name": "MECH"},
        {"unit_id": 761, "name": "MECH EQPT"},
        {"unit_id": 762, "name": "MECH.SHOP"},
        {"unit_id": 763, "name": "MECHANICAL"},
        {"unit_id": 764, "name": "MELTING"},
        {"unit_id": 765, "name": "MELTING SEC."},
        {"unit_id": 766, "name": "MILL"},
        {"unit_id": 1411, "name": "MILL PROPER"},
        {"unit_id": 767, "name": "MILL STAND"},
        {"unit_id": 768, "name": "MILLING M/C"},
        {"unit_id": 769, "name": "MILLS"},
        {"unit_id": 770, "name": "MINES"},
        {"unit_id": 771, "name": "MISC EQPT"},
        {"unit_id": 772, "name": "MISC."},
        {"unit_id": 773, "name": "MIXERS"},
        {"unit_id": 774, "name": "MIXING DRUM"},
        {"unit_id": 775, "name": "MOBILE EQPT"},
        {"unit_id": 776, "name": "MONORAIL"},
        {"unit_id": 777, "name": "MOTOR HOUSE"},
        {"unit_id": 778, "name": "MOULD"},
        {"unit_id": 779, "name": "MOULD FLOOR"},
        {"unit_id": 780, "name": "MOULD INGOT"},
        {"unit_id": 781, "name": "MOULD LADDLE"},
        {"unit_id": 782, "name": "MOULD SYSTEM"},
        {"unit_id": 783, "name": "MOULD&CORE"},
        {"unit_id": 784, "name": "MOULDING SEC"},
        {"unit_id": 785, "name": "MP.BOILER"},
        {"unit_id": 786, "name": "MPB-1&2"},
        {"unit_id": 787, "name": "MPB-3"},
        {"unit_id": 788, "name": "MS"},
        {"unit_id": 789, "name": "MSDS-3"},
        {"unit_id": 1460, "name": "MSRS"},
        {"unit_id": 790, "name": "MT"},
        {"unit_id": 791, "name": "MUD GUN"},
        {"unit_id": 792, "name": "MUD PREPARE"},
        {"unit_id": 793, "name": "MUDGUN"},
        {"unit_id": 794, "name": "N.BLOWER"},
        {"unit_id": 795, "name": "N.COMPRESSOR"},
        {"unit_id": 796, "name": "N.D.SYSTEM"},
        {"unit_id": 797, "name": "N.F.C M/C"},
        {"unit_id": 798, "name": "N.F.FOUNDRY"},
        {"unit_id": 799, "name": "N.FCE"},
        {"unit_id": 800, "name": "N.FURNACE"},
        {"unit_id": 801, "name": "N.L.S.PLANT"},
        {"unit_id": 802, "name": "N.L.STONE"},
        {"unit_id": 803, "name": "N.LIME STONE"},
        {"unit_id": 804, "name": "N2 STORAGE"},
        {"unit_id": 805, "name": "NAPHTHALENE"},
        {"unit_id": 806, "name": "NEPTHA PLANT"},
        {"unit_id": 1438, "name": "NEW C.S. PLANT"},
        {"unit_id": 1490, "name": "NEW CCD"},
        {"unit_id": 1515, "name": "NEW CHP"},
        {"unit_id": 1516, "name": "NEW COAL HANDLING PLANT"},
        {"unit_id": 807, "name": "NEW FURNACE"},
        {"unit_id": 808, "name": "NEW G.C.P"},
        {"unit_id": 809, "name": "NEW GCP"},
        {"unit_id": 1459, "name": "NEW HMDS"},
        {"unit_id": 1451, "name": "NEW HSM"},
        {"unit_id": 1454, "name": "NEW PCM"},
        {"unit_id": 1373, "name": "NEW PLATE MILL"},
        {"unit_id": 810, "name": "NEW W.B.FCE"},
        {"unit_id": 811, "name": "NH3 RECOVERY"},
        {"unit_id": 812, "name": "NITRIC ACID"},
        {"unit_id": 813, "name": "NITRO LIME"},
        {"unit_id": 814, "name": "NORM.FCE"},
        {"unit_id": 815, "name": "NORMALIZING"},
        {"unit_id": 816, "name": "NRP-2"},
        {"unit_id": 817, "name": "O.H.FCE"},
        {"unit_id": 818, "name": "O.L.EQPT"},
        {"unit_id": 819, "name": "O.R.PLANT"},
        {"unit_id": 820, "name": "O.T.C"},
        {"unit_id": 821, "name": "O.W. M/C"},
        {"unit_id": 822, "name": "OBBP"},
        {"unit_id": 823, "name": "OIL CELLER"},
        {"unit_id": 824, "name": "OIL PUMP"},
        {"unit_id": 825, "name": "OIL REFINING"},
        {"unit_id": 826, "name": "OIL TRANS"},
        {"unit_id": 1370, "name": "ORE LOADING"},
        {"unit_id": 827, "name": "OVEN"},
        {"unit_id": 828, "name": "OVEN AUX"},
        {"unit_id": 829, "name": "OVEN AUXL"},
        {"unit_id": 830, "name": "OVEN HEATING"},
        {"unit_id": 831, "name": "OVEN M/CS"},
        {"unit_id": 832, "name": "OVEN STR"},
        {"unit_id": 833, "name": "OVENS"},
        {"unit_id": 834, "name": "OXY.& S.LINE"},
        {"unit_id": 835, "name": "OXY.COMPRESS"},
        {"unit_id": 836, "name": "OXY.S.LINE"},
        {"unit_id": 837, "name": "OXYGEN PLANT"},
        {"unit_id": 838, "name": "P MIX DRUM"},
        {"unit_id": 839, "name": "P&I DIAGRAM"},
        {"unit_id": 840, "name": "P&T MELTING"},
        {"unit_id": 841, "name": "P..G.PLANT"},
        {"unit_id": 842, "name": "P.ANNEALING"},
        {"unit_id": 1419, "name": "P.B.BUILDING"},
        {"unit_id": 843, "name": "P.C.DEVICE"},
        {"unit_id": 844, "name": "P.CONVEYOR"},
        {"unit_id": 845, "name": "P.COOLER"},
        {"unit_id": 846, "name": "P.CRUSHING"},
        {"unit_id": 847, "name": "P.DRUM"},
        {"unit_id": 848, "name": "P.FEEDER"},
        {"unit_id": 849, "name": "P.L.S.QUARRY"},
        {"unit_id": 850, "name": "P.M.D"},
        {"unit_id": 851, "name": "P.M.P.HOUSE"},
        {"unit_id": 852, "name": "P.M.T.HOUSE"},
        {"unit_id": 853, "name": "P.MACHINERY"},
        {"unit_id": 854, "name": "P.MIXER"},
        {"unit_id": 855, "name": "P.N & U.COL"},
        {"unit_id": 856, "name": "P.W.MACHINE"},
        {"unit_id": 1403, "name": "PADDLE DRIVE"},
        {"unit_id": 857, "name": "PALLETIZING"},
        {"unit_id": 858, "name": "PATTERN SHOP"},
        {"unit_id": 859, "name": "PBCC"},
        {"unit_id": 1414, "name": "PBS"},
        {"unit_id": 1430, "name": "PCI"},
        {"unit_id": 860, "name": "PCM"},
        {"unit_id": 861, "name": "PELLET DRUM"},
        {"unit_id": 862, "name": "PELLETISING"},
        {"unit_id": 863, "name": "PENSTOCKS"},
        {"unit_id": 864, "name": "PGP"},
        {"unit_id": 865, "name": "PICKLING"},
        {"unit_id": 866, "name": "PICKLING-2"},
        {"unit_id": 867, "name": "PIE LINE"},
        {"unit_id": 868, "name": "PILER-1"},
        {"unit_id": 869, "name": "PILERS"},
        {"unit_id": 1388, "name": "PILING EQUIPMENT"},
        {"unit_id": 870, "name": "PINCH ROLL"},
        {"unit_id": 871, "name": "PIPE CLEAN"},
        {"unit_id": 872, "name": "PIPE CONVEY"},
        {"unit_id": 873, "name": "PIPE END BEVELLING M/C"},
        {"unit_id": 1532, "name": "PIPE FLUSHING M/C"},
        {"unit_id": 874, "name": "PIPE LINES"},
        {"unit_id": 875, "name": "PIPE MAKING"},
        {"unit_id": 876, "name": "PIPE WORK"},
        {"unit_id": 877, "name": "PIPELINE"},
        {"unit_id": 878, "name": "PIPES"},
        {"unit_id": 879, "name": "PIPING"},
        {"unit_id": 880, "name": "PIPING GENL"},
        {"unit_id": 881, "name": "PIT BINS"},
        {"unit_id": 882, "name": "PIT SIDE"},
        {"unit_id": 44, "name": "PKD"},
        {"unit_id": 883, "name": "PL"},
        {"unit_id": 884, "name": "PL-1"},
        {"unit_id": 885, "name": "PL-1&2"},
        {"unit_id": 886, "name": "PL-2"},
        {"unit_id": 1486, "name": "PLANNO MILLER"},
        {"unit_id": 1395, "name": "PLATE COOLING SYSTEM"},
        {"unit_id": 1405, "name": "PLATE MARKING & PUNCHING M/C"},
        {"unit_id": 887, "name": "PLATE MILL"},
        {"unit_id": 1390, "name": "PLATE YARD ROLLER TABLES"},
        {"unit_id": 888, "name": "PLDQ"},
        {"unit_id": 889, "name": "PLOUGH FDR"},
        {"unit_id": 890, "name": "PM"},
        {"unit_id": 891, "name": "PM P.HOUSE"},
        {"unit_id": 892, "name": "PM S.P.PH"},
        {"unit_id": 893, "name": "PM T.HOUSE"},
        {"unit_id": 894, "name": "PMP HOUSE"},
        {"unit_id": 1450, "name": "POKING DOOR"},
        {"unit_id": 895, "name": "PORTABLE M/C"},
        {"unit_id": 897, "name": "PRE-COOLING"},
        {"unit_id": 896, "name": "PRECIPITATOR"},
        {"unit_id": 1455, "name": "PRIMARY DESCALER"},
        {"unit_id": 898, "name": "PROCESS ESP"},
        {"unit_id": 899, "name": "PROCESSING"},
        {"unit_id": 1487, "name": "PROPANE PLANT"},
        {"unit_id": 900, "name": "PROPERTN BIN"},
        {"unit_id": 901, "name": "PUG MILL"},
        {"unit_id": 1401, "name": "PULPITS"},
        {"unit_id": 902, "name": "PUMP HOUSE"},
        {"unit_id": 903, "name": "PUMPS"},
        {"unit_id": 904, "name": "PURE ARGON"},
        {"unit_id": 905, "name": "PURIFICATION"},
        {"unit_id": 906, "name": "PURNAPANI"},
        {"unit_id": 907, "name": "PUSHER CAR"},
        {"unit_id": 908, "name": "Q.CAR"},
        {"unit_id": 909, "name": "Q.R.CHANGING"},
        {"unit_id": 910, "name": "QUENCH INST."},
        {"unit_id": 911, "name": "QUENCH PLATE"},
        {"unit_id": 912, "name": "QUENCH TOWER"},
        {"unit_id": 913, "name": "QUENCH.CAR"},
        {"unit_id": 914, "name": "QUENCH.PLANT"},
        {"unit_id": 915, "name": "QUENCHIING"},
        {"unit_id": 916, "name": "QUENCHING CAR"},
        {"unit_id": 917, "name": "R MILL"},
        {"unit_id": 918, "name": "R.CAR"},
        {"unit_id": 919, "name": "R.CHANGING"},
        {"unit_id": 920, "name": "R.COLD MILL"},
        {"unit_id": 921, "name": "R.COMPRESSOR"},
        {"unit_id": 922, "name": "R.D.M/C"},
        {"unit_id": 923, "name": "R.DRILL M/C"},
        {"unit_id": 924, "name": "R.F.CUTTER"},
        {"unit_id": 925, "name": "R.F.FCE 5&6"},
        {"unit_id": 926, "name": "R.FCE.5&6"},
        {"unit_id": 927, "name": "R.G.M/C"},
        {"unit_id": 928, "name": "R.G.MILL"},
        {"unit_id": 929, "name": "R.GM/C"},
        {"unit_id": 930, "name": "R.GRIND M/C"},
        {"unit_id": 1369, "name": "R.H. GAS"},
        {"unit_id": 932, "name": "R.H.FCE-3"},
        {"unit_id": 933, "name": "R.H.FEC"},
        {"unit_id": 934, "name": "R.H.FURNACE"},
        {"unit_id": 935, "name": "R.M DESPATCH"},
        {"unit_id": 937, "name": "R.M.P.HOUSE"},
        {"unit_id": 938, "name": "R.M.P.STN"},
        {"unit_id": 939, "name": "R.M.STREAM"},
        {"unit_id": 940, "name": "R.M.SYSTEM"},
        {"unit_id": 941, "name": "R.M.T.HOUSE"},
        {"unit_id": 942, "name": "R.MILL"},
        {"unit_id": 943, "name": "R.S.SYSTEM"},
        {"unit_id": 944, "name": "R.SINGALING"},
        {"unit_id": 945, "name": "R.STAND"},
        {"unit_id": 946, "name": "R.STAND-1"},
        {"unit_id": 947, "name": "R.STAND-2"},
        {"unit_id": 948, "name": "R.STOCK"},
        {"unit_id": 949, "name": "R.T.M/C"},
        {"unit_id": 950, "name": "R.TABLE"},
        {"unit_id": 951, "name": "R.TROLLEY"},
        {"unit_id": 952, "name": "R.WINTCH"},
        {"unit_id": 953, "name": "R/0"},
        {"unit_id": 954, "name": "R0"},
        {"unit_id": 955, "name": "R0/V0"},
        {"unit_id": 956, "name": "R1"},
        {"unit_id": 957, "name": "R2"},
        {"unit_id": 958, "name": "RADIAL D.M/C"},
        {"unit_id": 959, "name": "RAIL CRANE"},
        {"unit_id": 960, "name": "RAMCAR"},
        {"unit_id": 961, "name": "RATARY KILN"},
        {"unit_id": 962, "name": "RAW GAS MAIN"},
        {"unit_id": 963, "name": "RAW MATERIAL"},
        {"unit_id": 964, "name": "RC(M)"},
        {"unit_id": 965, "name": "RD M/C"},
        {"unit_id": 931, "name": "RE-HEATING FURNACE"},
        {"unit_id": 966, "name": "REBUILDING"},
        {"unit_id": 1482, "name": "RECLAIMER"},
        {"unit_id": 967, "name": "RECOILER"},
        {"unit_id": 968, "name": "REDUCING FCE"},
        {"unit_id": 970, "name": "REFRACTORIES"},
        {"unit_id": 969, "name": "REFRACTRIES"},
        {"unit_id": 971, "name": "REFRIGERATN"},
        {"unit_id": 972, "name": "REFRSCTORIES"},
        {"unit_id": 973, "name": "REGENERATION"},
        {"unit_id": 1377, "name": "REHEATING FURNACE-1"},
        {"unit_id": 974, "name": "RELINE EQPT"},
        {"unit_id": 975, "name": "RELINING"},
        {"unit_id": 976, "name": "REPAIR & ST"},
        {"unit_id": 977, "name": "REPAIR HOIST"},
        {"unit_id": 978, "name": "REPAIR POST"},
        {"unit_id": 979, "name": "REPAIR SHOP"},
        {"unit_id": 980, "name": "REV.WINCH"},
        {"unit_id": 981, "name": "REVERSE MILL"},
        {"unit_id": 982, "name": "REVERSING"},
        {"unit_id": 983, "name": "RH FCE 5&6"},
        {"unit_id": 1361, "name": "RH FURNACE"},
        {"unit_id": 1440, "name": "RHOB"},
        {"unit_id": 984, "name": "RILLING MILL"},
        {"unit_id": 985, "name": "RM"},
        {"unit_id": 1503, "name": "RM BUR"},
        {"unit_id": 1534, "name": "RM DESCALING"},
        {"unit_id": 936, "name": "RM EDGER"},
        {"unit_id": 1522, "name": "RM ENTRY SIDE GUIDE"},
        {"unit_id": 1497, "name": "RM ENTRY TABLE"},
        {"unit_id": 1517, "name": "RM PROPER"},
        {"unit_id": 986, "name": "RM PUMPHOUSE"},
        {"unit_id": 1502, "name": "RM WR"},
        {"unit_id": 987, "name": "RMT HOUSE"},
        {"unit_id": 988, "name": "RO"},
        {"unit_id": 989, "name": "RO/VOATION"},
        {"unit_id": 990, "name": "ROAD VEHICLE"},
        {"unit_id": 991, "name": "ROCK RUNNER"},
        {"unit_id": 992, "name": "ROD MILL"},
        {"unit_id": 993, "name": "ROD&RP GATE"},
        {"unit_id": 994, "name": "ROLL CHANGE"},
        {"unit_id": 995, "name": "ROLL SHOP"},
        {"unit_id": 996, "name": "ROLL STAND"},
        {"unit_id": 997, "name": "ROLL STOCK"},
        {"unit_id": 998, "name": "ROLLER STAND"},
        {"unit_id": 999, "name": "ROLLER TABLE"},
        {"unit_id": 1362, "name": "ROLLING MILL"},
        {"unit_id": 1000, "name": "ROLLS"},
        {"unit_id": 1001, "name": "ROLLSTOCK"},
        {"unit_id": 1002, "name": "ROOLING MILL"},
        {"unit_id": 1372, "name": "ROPE DRUM"},
        {"unit_id": 1363, "name": "ROTARY KILN"},
        {"unit_id": 1003, "name": "ROTATRY KILN"},
        {"unit_id": 1004, "name": "ROUGH.STAND"},
        {"unit_id": 1005, "name": "ROUGHING MILL"},
        {"unit_id": 1006, "name": "ROUGHING STD"},
        {"unit_id": 1007, "name": "ROUGHING-1"},
        {"unit_id": 1008, "name": "RP HOUSE"},
        {"unit_id": 1009, "name": "RS(E)"},
        {"unit_id": 1010, "name": "RS(M)"},
        {"unit_id": 1011, "name": "RS(MECH)"},
        {"unit_id": 1012, "name": "RS(S)"},
        {"unit_id": 1013, "name": "RSM"},
        {"unit_id": 1014, "name": "RUNOUT EQPT"},
        {"unit_id": 1520, "name": "RUNOUT TABLE"},
        {"unit_id": 1015, "name": "S S COMPLEX"},
        {"unit_id": 1016, "name": "S STEEL"},
        {"unit_id": 1017, "name": "S&M DRIER"},
        {"unit_id": 1018, "name": "S&O LINES"},
        {"unit_id": 1019, "name": "S&S DISPOSAL"},
        {"unit_id": 1020, "name": "S&WATER MAIN"},
        {"unit_id": 1021, "name": "S. DISPOSAL"},
        {"unit_id": 1022, "name": "S.&02 P.LINE"},
        {"unit_id": 1023, "name": "S.A.PLANT"},
        {"unit_id": 1024, "name": "S.B. M/C"},
        {"unit_id": 1025, "name": "S.B.G.M/C"},
        {"unit_id": 1026, "name": "S.B.M/C"},
        {"unit_id": 1027, "name": "S.B.P-1&2"},
        {"unit_id": 1028, "name": "S.B.PLANT"},
        {"unit_id": 1029, "name": "S.BEARING"},
        {"unit_id": 1030, "name": "S.BLAST M/C"},
        {"unit_id": 1031, "name": "S.BLSTG.M/C"},
        {"unit_id": 1032, "name": "S.BREAKER"},
        {"unit_id": 1033, "name": "S.C.DEVICE"},
        {"unit_id": 1034, "name": "S.C.TRANSFER"},
        {"unit_id": 1035, "name": "S.COOLER"},
        {"unit_id": 1036, "name": "S.D.SYSTEM"},
        {"unit_id": 1037, "name": "S.DISPOSAL"},
        {"unit_id": 1038, "name": "S.DISTRIBUTE"},
        {"unit_id": 1039, "name": "S.E.ASU-4"},
        {"unit_id": 1040, "name": "S.GAS PLANT"},
        {"unit_id": 1041, "name": "S.L.INDICATE"},
        {"unit_id": 1042, "name": "S.O2 LINE"},
        {"unit_id": 1043, "name": "S.P.PLANT"},
        {"unit_id": 1044, "name": "S.P.SITE LAB"},
        {"unit_id": 1045, "name": "S.PIT"},
        {"unit_id": 1046, "name": "S.POND"},
        {"unit_id": 1047, "name": "S.PRESS"},
        {"unit_id": 1048, "name": "S.R.CRUSHER"},
        {"unit_id": 1049, "name": "S.R.FCE"},
        {"unit_id": 1050, "name": "S.S.COMPLEX"},
        {"unit_id": 1052, "name": "S.S.LINE"},
        {"unit_id": 1054, "name": "S.S.STATION"},
        {"unit_id": 1055, "name": "S.S.VAR"},
        {"unit_id": 1056, "name": "S.STATION"},
        {"unit_id": 1057, "name": "S.T.CAR"},
        {"unit_id": 1058, "name": "S.T.STAND"},
        {"unit_id": 1059, "name": "S.TRANSFER"},
        {"unit_id": 1060, "name": "S.TRIMMING"},
        {"unit_id": 1061, "name": "S.YARD"},
        {"unit_id": 1062, "name": "S.YARD EQPT"},
        {"unit_id": 1513, "name": "SAMPLE SHEAR"},
        {"unit_id": 1063, "name": "SAMPLING"},
        {"unit_id": 1064, "name": "SAMPLING STN"},
        {"unit_id": 1065, "name": "SAND P.PLANT"},
        {"unit_id": 1066, "name": "SAND PLANT"},
        {"unit_id": 1067, "name": "SAND PREPARE"},
        {"unit_id": 1068, "name": "SAND PREPN"},
        {"unit_id": 1069, "name": "SATURATOR"},
        {"unit_id": 1458, "name": "SCALE CAR"},
        {"unit_id": 1070, "name": "SCALE WASHER"},
        {"unit_id": 1071, "name": "SCRAP CAR"},
        {"unit_id": 1378, "name": "SCRAP CONVEYOR"},
        {"unit_id": 1072, "name": "SCRAP DISPOS"},
        {"unit_id": 1466, "name": "SCRAP PIT"},
        {"unit_id": 1073, "name": "SCRAP SHEAR"},
        {"unit_id": 1074, "name": "SCREEN"},
        {"unit_id": 1075, "name": "SCREEN HOUSE"},
        {"unit_id": 1076, "name": "SCREEN PLATE"},
        {"unit_id": 1077, "name": "SCREEN STN"},
        {"unit_id": 1078, "name": "SCREENING"},
        {"unit_id": 1079, "name": "SCREW CONV"},
        {"unit_id": 1080, "name": "SEAM WELDER"},
        {"unit_id": 1081, "name": "SECTOR-2"},
        {"unit_id": 1082, "name": "SECTOR-20"},
        {"unit_id": 1083, "name": "SECTOR-8"},
        {"unit_id": 1084, "name": "SERVICE LINE"},
        {"unit_id": 1085, "name": "SERVICES"},
        {"unit_id": 1051, "name": "SEWAGE SYSTEM"},
        {"unit_id": 1086, "name": "SGP"},
        {"unit_id": 1087, "name": "SHAFT KILN"},
        {"unit_id": 1088, "name": "SHEAR"},
        {"unit_id": 1089, "name": "SHEAR&CROP"},
        {"unit_id": 1090, "name": "SHEARING"},
        {"unit_id": 1091, "name": "SHEET SHEARING"},
        {"unit_id": 1092, "name": "SHELL"},
        {"unit_id": 1093, "name": "SHIPPING"},
        {"unit_id": 1094, "name": "SHOT BLAST"},
        {"unit_id": 1519, "name": "SHUTTLE CAR"},
        {"unit_id": 1404, "name": "SIDE ARM CHARGER"},
        {"unit_id": 1095, "name": "SIDE TRIM"},
        {"unit_id": 1096, "name": "SIDE TRIMMER"},
        {"unit_id": 1097, "name": "SIGNALLING"},
        {"unit_id": 1526, "name": "SILENCER"},
        {"unit_id": 1436, "name": "SILO BUILDING"},
        {"unit_id": 1098, "name": "SINT BREAKER"},
        {"unit_id": 1099, "name": "SINT COOLER"},
        {"unit_id": 1100, "name": "SINT CRUSHER"},
        {"unit_id": 1101, "name": "SINT MACHINE"},
        {"unit_id": 1102, "name": "SINT MIXING"},
        {"unit_id": 1104, "name": "SINT STORAGE"},
        {"unit_id": 1105, "name": "SINT.COOLER"},
        {"unit_id": 1492, "name": "SINTER BUNKER"},
        {"unit_id": 1107, "name": "SINTER M/C"},
        {"unit_id": 1108, "name": "SINTER PIT"},
        {"unit_id": 1106, "name": "SINTER SCREEN"},
        {"unit_id": 1103, "name": "SINTER. SCREEN"},
        {"unit_id": 1109, "name": "SINTER STORE"},
        {"unit_id": 1110, "name": "SINTERING"},
        {"unit_id": 1111, "name": "SIZING"},
        {"unit_id": 1112, "name": "SIZING STAND"},
        {"unit_id": 1113, "name": "SKIN PASS"},
        {"unit_id": 1114, "name": "SKIP"},
        {"unit_id": 1115, "name": "SKIP CAR"},
        {"unit_id": 1116, "name": "SKIP HOIST"},
        {"unit_id": 1117, "name": "SKIP WINCH"},
        {"unit_id": 1119, "name": "SL-1&2"},
        {"unit_id": 1118, "name": "SL.INDICATOR"},
        {"unit_id": 1481, "name": "SLAB CAR"},
        {"unit_id": 1053, "name": "SLAB CASTING SHOP"},
        {"unit_id": 1120, "name": "SLAB COOLING"},
        {"unit_id": 1121, "name": "SLAB STORAGE"},
        {"unit_id": 1122, "name": "SLAB TRANS"},
        {"unit_id": 1499, "name": "SLAB WEIGHER"},
        {"unit_id": 1376, "name": "SLAB YARD"},
        {"unit_id": 1123, "name": "SLAG CAR"},
        {"unit_id": 1124, "name": "SLAG PIT"},
        {"unit_id": 1125, "name": "SLAG POT&CAR"},
        {"unit_id": 1126, "name": "SLAG POTS"},
        {"unit_id": 1127, "name": "SLAG YARD"},
        {"unit_id": 1128, "name": "SLAGPOT&CARS"},
        {"unit_id": 1495, "name": "SLEDGE SLIDE GUIDE"},
        {"unit_id": 1129, "name": "SLITNG.LINE"},
        {"unit_id": 1130, "name": "SLITTER"},
        {"unit_id": 1131, "name": "SLITTER-1"},
        {"unit_id": 1132, "name": "SLITTER-2"},
        {"unit_id": 1133, "name": "SLITTING"},
        {"unit_id": 1134, "name": "SLITTING-1"},
        {"unit_id": 1135, "name": "SMS"},
        {"unit_id": 1136, "name": "SMS P.HOUSE"},
        {"unit_id": 1137, "name": "SMS-1"},
        {"unit_id": 1138, "name": "SMS-1 EXTN"},
        {"unit_id": 1139, "name": "SMS-2"},
        {"unit_id": 1140, "name": "SMS-2(BOF)"},
        {"unit_id": 1141, "name": "SOAKING PIT"},
        {"unit_id": 1477, "name": "SOLAR POWER PLANT"},
        {"unit_id": 1142, "name": "SP"},
        {"unit_id": 1143, "name": "SP-1"},
        {"unit_id": 1144, "name": "SP-2"},
        {"unit_id": 1145, "name": "SP-3"},
        {"unit_id": 1146, "name": "SPP"},
        {"unit_id": 1147, "name": "SS COMPRESS"},
        {"unit_id": 1148, "name": "SSD"},
        {"unit_id": 1149, "name": "SSL-1&2"},
        {"unit_id": 1150, "name": "SSM"},
        {"unit_id": 1151, "name": "SSP"},
        {"unit_id": 1153, "name": "STACKER"},
        {"unit_id": 1154, "name": "STACKER BOOM"},
        {"unit_id": 1415, "name": "STACKER CUM RECLAIMER"},
        {"unit_id": 1155, "name": "STACKS"},
        {"unit_id": 1156, "name": "STAMP & OXY"},
        {"unit_id": 1157, "name": "STANDARD"},
        {"unit_id": 1158, "name": "STD.DESIGN"},
        {"unit_id": 1159, "name": "STEAM & OXNG"},
        {"unit_id": 1160, "name": "STEAM BLOWER"},
        {"unit_id": 1161, "name": "STEAM BOILER"},
        {"unit_id": 1162, "name": "STEAM LINE"},
        {"unit_id": 1163, "name": "STEAM&OXYGEN"},
        {"unit_id": 1164, "name": "STEEL CAR"},
        {"unit_id": 1165, "name": "STEEL FDY"},
        {"unit_id": 1525, "name": "STG"},
        {"unit_id": 1166, "name": "STOCK HOUSE"},
        {"unit_id": 1167, "name": "STOCK LINE"},
        {"unit_id": 1168, "name": "STOPPERS"},
        {"unit_id": 1169, "name": "STORES"},
        {"unit_id": 1170, "name": "STOVES"},
        {"unit_id": 1171, "name": "STP"},
        {"unit_id": 1441, "name": "STRAIGHTENER"},
        {"unit_id": 1172, "name": "STRIP PREPN"},
        {"unit_id": 1173, "name": "STRIPPER"},
        {"unit_id": 1174, "name": "STRL SHOP"},
        {"unit_id": 1175, "name": "STRUCTURAL"},
        {"unit_id": 1176, "name": "SUB-STATION"},
        {"unit_id": 1152, "name": "SUB-STORE"},
        {"unit_id": 1177, "name": "SULPHATE"},
        {"unit_id": 1178, "name": "SULPHUR ACID"},
        {"unit_id": 1179, "name": "SUMP AREA"},
        {"unit_id": 1180, "name": "SUMP PUMP"},
        {"unit_id": 1181, "name": "SURFACE PLAN"},
        {"unit_id": 1182, "name": "SWITCH PANEL"},
        {"unit_id": 1183, "name": "SYNTHESIS"},
        {"unit_id": 1184, "name": "T&L.HANDLG"},
        {"unit_id": 1185, "name": "T&O HEATING"},
        {"unit_id": 1186, "name": "T.A"},
        {"unit_id": 1187, "name": "T.A & DECARB"},
        {"unit_id": 1188, "name": "T.A SET"},
        {"unit_id": 1189, "name": "T.A.LINE"},
        {"unit_id": 1190, "name": "T.ALTERNATE"},
        {"unit_id": 1191, "name": "T.ALTERNATOR"},
        {"unit_id": 1192, "name": "T.ANNEALING"},
        {"unit_id": 1193, "name": "T.B.STACKER"},
        {"unit_id": 1194, "name": "T.C.EQIPT"},
        {"unit_id": 1195, "name": "T.C.M/C"},
        {"unit_id": 1196, "name": "T.DISTLTION"},
        {"unit_id": 1197, "name": "T.DISTRIBUTE"},
        {"unit_id": 1198, "name": "T.DRILL M/C"},
        {"unit_id": 1199, "name": "T.G.M/C"},
        {"unit_id": 1200, "name": "T.GRINDER"},
        {"unit_id": 1201, "name": "T.H&D.M/C"},
        {"unit_id": 1202, "name": "T.H&S.STAND"},
        {"unit_id": 1203, "name": "T.H.D.M/C"},
        {"unit_id": 1204, "name": "T.H.MUDGUN"},
        {"unit_id": 1205, "name": "T.LADLE"},
        {"unit_id": 1206, "name": "T.MILL"},
        {"unit_id": 1207, "name": "T.P. HOUSE"},
        {"unit_id": 1208, "name": "T.P.HOUSE-2"},
        {"unit_id": 1209, "name": "T.PRESS"},
        {"unit_id": 1210, "name": "T.PUMP HOUSE"},
        {"unit_id": 1211, "name": "T.SIGNALING"},
        {"unit_id": 1212, "name": "T.TABLE"},
        {"unit_id": 1213, "name": "TA & DECARB"},
        {"unit_id": 1214, "name": "TA-4"},
        {"unit_id": 1215, "name": "TANDEM MILL"},
        {"unit_id": 1216, "name": "TANK STORAGE"},
        {"unit_id": 1217, "name": "TAR DIST"},
        {"unit_id": 1218, "name": "TAR DISTILE"},
        {"unit_id": 1219, "name": "TARKERA"},
        {"unit_id": 1467, "name": "TBDB"},
        {"unit_id": 1220, "name": "TEEMING"},
        {"unit_id": 1221, "name": "TEL COMM ENG"},
        {"unit_id": 1222, "name": "TELE&SIGNAL"},
        {"unit_id": 1223, "name": "TELECOM"},
        {"unit_id": 1224, "name": "TEMER KILN"},
        {"unit_id": 1225, "name": "TEMP FCE"},
        {"unit_id": 1226, "name": "TEMP FURNACE"},
        {"unit_id": 1227, "name": "TEMP KILN"},
        {"unit_id": 1228, "name": "TEMP.FURNCE"},
        {"unit_id": 1229, "name": "TEMPER FCE"},
        {"unit_id": 1230, "name": "TEMPER KILN"},
        {"unit_id": 1231, "name": "TENDEM MILL"},
        {"unit_id": 1232, "name": "TENSA TOWN"},
        {"unit_id": 1233, "name": "TEST HOUSE"},
        {"unit_id": 17, "name": "TEST LAB"},
        {"unit_id": 1457, "name": "TEST LOAD CAR"},
        {"unit_id": 1528, "name": "TEST PIECE SHEAR"},
        {"unit_id": 1234, "name": "TEST PRESS"},
        {"unit_id": 1235, "name": "TEST&FINISH"},
        {"unit_id": 1236, "name": "TESTING"},
        {"unit_id": 1237, "name": "TESTING M/C"},
        {"unit_id": 1238, "name": "TH.DRILL M/C"},
        {"unit_id": 1239, "name": "THAWING SEC"},
        {"unit_id": 1240, "name": "THAWING STN"},
        {"unit_id": 1241, "name": "THM PREPARE"},
        {"unit_id": 1242, "name": "THMP PLANT"},
        {"unit_id": 1243, "name": "TILTER"},
        {"unit_id": 1244, "name": "TILTING"},
        {"unit_id": 1245, "name": "TIPPLER"},
        {"unit_id": 1409, "name": "TLC"},
        {"unit_id": 1246, "name": "TOP-2"},
        {"unit_id": 1247, "name": "TORTY PRESS"},
        {"unit_id": 1248, "name": "TOWN"},
        {"unit_id": 1249, "name": "TOWNSHIP"},
        {"unit_id": 1250, "name": "TP HOUSE"},
        {"unit_id": 1251, "name": "TPH"},
        {"unit_id": 1252, "name": "TRACK HOPPER"},
        {"unit_id": 1253, "name": "TRACK SYSTEM"},
        {"unit_id": 1254, "name": "TRAFFIC"},
        {"unit_id": 1255, "name": "TRANSFER CAR"},
        {"unit_id": 1256, "name": "TRANSPORT"},
        {"unit_id": 1257, "name": "TRIM LINE"},
        {"unit_id": 1258, "name": "TRIMMING"},
        {"unit_id": 1259, "name": "TRIPPER"},
        {"unit_id": 1260, "name": "TUBRO BLOWER"},
        {"unit_id": 1261, "name": "TUMKELA"},
        {"unit_id": 1262, "name": "TUNDISH"},
        {"unit_id": 1263, "name": "TUNDISH CARS"},
        {"unit_id": 1264, "name": "TURBINE"},
        {"unit_id": 1265, "name": "TURBO ALTER"},
        {"unit_id": 1266, "name": "TURBO BLOWER"},
        {"unit_id": 1267, "name": "TURBO COMPR"},
        {"unit_id": 1268, "name": "TURK'S HEAD"},
        {"unit_id": 1464, "name": "TUYERE STOCK"},
        {"unit_id": 1269, "name": "U.H.COOLING"},
        {"unit_id": 1270, "name": "U.S.T.M/C"},
        {"unit_id": 1271, "name": "UNCOILER"},
        {"unit_id": 1514, "name": "UNCOILER MANDREL"},
        {"unit_id": 1488, "name": "UNIT-1"},
        {"unit_id": 1410, "name": "UNIT-3"},
        {"unit_id": 1272, "name": "UNIT-4"},
        {"unit_id": 1417, "name": "UNIVERSAL CAGE"},
        {"unit_id": 1444, "name": "UNIVERSAL SPINDLES"},
        {"unit_id": 1273, "name": "UNLOAD STORE"},
        {"unit_id": 1274, "name": "UNLOADING"},
        {"unit_id": 1462, "name": "UNWIND MANDREL"},
        {"unit_id": 1275, "name": "UPCOILER"},
        {"unit_id": 1276, "name": "UPENDER"},
        {"unit_id": 1491, "name": "UPPER KNIFE SLEDGE"},
        {"unit_id": 1383, "name": "UST TESTING M/C"},
        {"unit_id": 1277, "name": "UTILITY"},
        {"unit_id": 1278, "name": "UTILITY PIPE"},
        {"unit_id": 1279, "name": "V&DE SYSTEM"},
        {"unit_id": 1280, "name": "V.B. M/C"},
        {"unit_id": 1281, "name": "V.BORING M/C"},
        {"unit_id": 1282, "name": "V.S.BREAKER"},
        {"unit_id": 1283, "name": "V.SCREEN"},
        {"unit_id": 1284, "name": "V/0"},
        {"unit_id": 1364, "name": "V0/R0"},
        {"unit_id": 1285, "name": "VACCUM CRANE"},
        {"unit_id": 1365, "name": "VALVE"},
        {"unit_id": 1286, "name": "VALVES"},
        {"unit_id": 1287, "name": "VAPORISATION"},
        {"unit_id": 1288, "name": "VAR"},
        {"unit_id": 1500, "name": "VE CHOCK ASSEMBLY"},
        {"unit_id": 1498, "name": "VE PROPER"},
        {"unit_id": 1290, "name": "VENTI & AIR"},
        {"unit_id": 1291, "name": "VENTILATION"},
        {"unit_id": 1397, "name": "VENTILATION SYSTEMS"},
        {"unit_id": 1292, "name": "VENTILATOR"},
        {"unit_id": 1293, "name": "VESSEL 66T"},
        {"unit_id": 1294, "name": "VESSELS"},
        {"unit_id": 1295, "name": "VIBRATORS"},
        {"unit_id": 1296, "name": "VIBRO FEEDER"},
        {"unit_id": 1297, "name": "VIBRO MILL"},
        {"unit_id": 1298, "name": "VIBRO SCREEN"},
        {"unit_id": 1299, "name": "VO"},
        {"unit_id": 1289, "name": "VOD/VAR"},
        {"unit_id": 1300, "name": "W SOFTENING"},
        {"unit_id": 1301, "name": "W&T PLATFORM"},
        {"unit_id": 1302, "name": "W.A.RECOVERY"},
        {"unit_id": 1303, "name": "W.B.FCE"},
        {"unit_id": 1304, "name": "W.B.FURNACE"},
        {"unit_id": 1305, "name": "W.C.P.HOUSE"},
        {"unit_id": 1306, "name": "W.C.STACK"},
        {"unit_id": 1307, "name": "W.C.SYSTEM"},
        {"unit_id": 1308, "name": "W.COOLING"},
        {"unit_id": 1309, "name": "W.D.SYSTEM"},
        {"unit_id": 1313, "name": "W.G-5"},
        {"unit_id": 1310, "name": "W.G.ESP"},
        {"unit_id": 1311, "name": "W.G.FAN"},
        {"unit_id": 1312, "name": "W.G.SYSTEM"},
        {"unit_id": 1314, "name": "W.H.RECOVERY"},
        {"unit_id": 1315, "name": "W.H.S"},
        {"unit_id": 1316, "name": "W.HANDLING"},
        {"unit_id": 1317, "name": "W.ROOL CHOCK"},
        {"unit_id": 1318, "name": "W.T.P"},
        {"unit_id": 1319, "name": "W.T.PLANT"},
        {"unit_id": 1320, "name": "W.TIPPLER"},
        {"unit_id": 1321, "name": "W.TIPPLER-4"},
        {"unit_id": 1322, "name": "W.TIPPLER-5"},
        {"unit_id": 1323, "name": "W.W.T.P."},
        {"unit_id": 1324, "name": "WAGON TIPLER"},
        {"unit_id": 1325, "name": "WALKING BEAM"},
        {"unit_id": 1326, "name": "WASTE GAS"},
        {"unit_id": 1327, "name": "WATER COOLNG"},
        {"unit_id": 1328, "name": "WATER MAIN"},
        {"unit_id": 1329, "name": "WATER MGT"},
        {"unit_id": 1330, "name": "WATER PUMP"},
        {"unit_id": 1331, "name": "WATER SYSTEM"},
        {"unit_id": 1394, "name": "WATER TREATMENT SYSTEM"},
        {"unit_id": 1332, "name": "WATER WHEEL"},
        {"unit_id": 1333, "name": "WDS"},
        {"unit_id": 1334, "name": "WEIGH BRIDGE"},
        {"unit_id": 1335, "name": "WEIGH FEEDER"},
        {"unit_id": 1473, "name": "WEIGHING M/C"},
        {"unit_id": 1336, "name": "WELD M/C"},
        {"unit_id": 1337, "name": "WELD M/C-2"},
        {"unit_id": 1338, "name": "WELD STAND"},
        {"unit_id": 1339, "name": "WELDER"},
        {"unit_id": 1340, "name": "WELDING M/C"},
        {"unit_id": 1341, "name": "WG 6,7,8 M/C"},
        {"unit_id": 1342, "name": "WG-3,4,5"},
        {"unit_id": 1343, "name": "WHARVES"},
        {"unit_id": 1344, "name": "WINCH HOUSE"},
        {"unit_id": 1345, "name": "WINCHES"},
        {"unit_id": 1346, "name": "WLEDING M/C"},
        {"unit_id": 1347, "name": "WORK ROLL"},
        {"unit_id": 1348, "name": "WORK SHOP"},
        {"unit_id": 1505, "name": "WR CHOCK ASSEMBLY"},
        {"unit_id": 1349, "name": "WRS"},
        {"unit_id": 1350, "name": "WTP"},
        {"unit_id": 1470, "name": "WTP-1"},
        {"unit_id": 1471, "name": "WTP-2"},
        {"unit_id": 1472, "name": "WTP-3"},
        {"unit_id": 1351, "name": "WWPP"},
        {"unit_id": 1352, "name": "WWTP"},
        {"unit_id": 1353, "name": "XRF"},
        {"unit_id": 1354, "name": "YARD EQPT"},
        {"unit_id": 1355, "name": "YARD PIPING"},
        {"unit_id": 1446, "name": "ZONE-VII"}
        ]
    for i in unit_list:
        name = i["name"]
        unit_id = i["unit_id"]
        Unit.objects.update_or_create(unit_id=unit_id, defaults={"name": name})


def create_title():
    data = [
        {
            
            "TITLE_ID" : "1",
            "TITLE": "STANDARDS COMMITTEE ON MECHANICAL DRIVES, IPSS 1:1"
        },
        {
            "TITLE_ID" : "2",
            "TITLE": "STANDARDS COMMITTEE ON BASIC STANDARDS & HYDRAULIC, PNEUMATIC & LUBRICATING EQIUPMENT IPSS 1:2"
        },
        {
            "TITLE_ID" : "3",
            "TITLE": "STANDARDS COMMITTEE ON ROTATING  ELECTRICAL MACHINARY, IPSS 1:3"
        },
        {
            "TITLE_ID" : "4",
            "TITLE": "STANDARDS COMMITTEE ON SWITCHGEARS & CONTROLGEARS, IPSS 1:4"
        },
        {
            "TITLE_ID" : "5",
            "TITLE": "STANDARDS COMMITTEE ON PUMPS & COMPRESSORS, IPSS 1:5(A)"
        },
        {
            "TITLE_ID" : "6",
            "TITLE": "STANDARDS COMMITTEE ON PIPES, FITING, VALUES AND PIPING LAYOUT, IPSS 1:6"
        },
        {
            "TITLE_ID" : "7",
            "TITLE": "STANDARDS COMMITTEE ON PAINTS AND PORTABLE MAINTENANCE EQUIPMENT, IPSS 1:7"
        },
        {
            "TITLE_ID" : "8",
            "TITLE": "STANDARDS COMMITTEE ON LIFTING  AND HOISTING EQUIPMENT, IPSS 1:8"
        },
        {
            "TITLE_ID" : "9",
            "TITLE": "STANDARDS COMMITTEE ON OILS & LUBRICANTS, IPSS 1:9"
        },
        {
            "TITLE_ID" : "10",
            "TITLE": "SATNDARDS COMMITTEE ON ELECTRICAL COMPONENTS & EQUIPMENT, IPSS 1:10"
        },
        {
            "TITLE_ID" : "11",
            "TITLE": "STANDARDS COMMITTEE ON PERSONNEL SAFETY APPLIANCES AND PROCEDURES, IPSS 1:11[Earlier 1:5(B)]"
        },
        {
            "TITLE_ID" : "12",
            "TITLE": "STANDARDS COMMITTEE ON STEEL PLANT LADDLES AND ROLLING STOCK, IPSS 2:1"
        },
        {
            "TITLE_ID" : "13",
            "TITLE": "STANDARDS COMMITTEE ON EOT CRANES, IPSS 2:2"
        },
        {
            "TITLE_ID" : "14",
            "TITLE": "STANDARDS COMMITTEE ON CONVEYORS , IPSS 2:3"
        },
        {
            "TITLE_ID" : "15",
            "TITLE": "STANDARDS COMMITTEE ON COKE OVENS, IPSS 2:4"
        },
        {
            "TITLE_ID" : "16",
            "TITLE": "STANDARDS COMMITTEE ON COMPUTERIZATION AND AUTOMATION, IPSS 2:7"
        },
        {
            "TITLE_ID" : "17",
            "TITLE": "SATNDARDS COMMITTEE ON MATERIALS MANAGEMENT, IPSS 3:2"
        },
        {
            "TITLE_ID" : "18",
            "TITLE": "STANDARDS COMMITTEE ON OPERATION & MAINTENANCE, IPSS 3:2"
        },
        {
            "TITLE_ID" : "19",
            "TITLE": "STANDARDS COMMITTEE ON INTEGRATED PROJECTS MANAGEMENTS, IPSS 3:3"
        }
    ]
    
    for i in data:
        title = i["TITLE"]
        title_id = i["TITLE_ID"]
        IPSSTitle.objects.update_or_create(title = title, defaults={"title_id":title_id})
        
        
def create_rsn_volume():
    data=[
        {
            "VOL_ID": "1",
            "VOL_NO": "VOLUME - 1",
            "VOL_TITLE": "GENERAL FUNDAMENTALS & DRAWING PRACTICES"
        },
        {   
            "VOL_ID": "2",
            "VOL_NO": "VOLUME - 1a",
            "VOL_TITLE": "GEARS & GEARBOXES"
        },
        {
            "VOL_ID": "3",
            "VOL_NO": "VOLUME - 2",
            "VOL_TITLE": "ENGINEERING MATERIALS"
        },
        {
            "VOL_ID": "4",
            "VOL_NO": "VOLUME - 3",
            "VOL_TITLE": "TOOLS"
        },
        {
            "VOL_ID": "5",
            "VOL_NO": "VOLUME - 4",
            "VOL_TITLE": "MACHINE ELEMENTS & MECHANISMS"
        },
        {
            "VOL_ID": "6",
            "VOL_NO": "VOLUME - 5",
            "VOL_TITLE": "FASTENERS"
        },
        {
            "VOL_ID": "7",
            "VOL_NO": "VOLUME - 6",
            "VOL_TITLE": "PIPES, FLANGES, HOSES & ACCESSORIES"
        },
        {
            "VOL_ID": "8",
            "VOL_NO": "VOLUME - 7",
            "VOL_TITLE": "CRANES AND LIFTING TACKLES"
        },
        {
            "VOL_ID": "9",
            "VOL_NO": "VOLUME -7a",
            "VOL_TITLE": "MATERIAL HANDLING"
        },
        {
            "VOL_ID": "10",
            "VOL_NO": "VOLUME - 8",
            "VOL_TITLE": "LUBRICATION , HYDRAULICS & PNEUMATICS"
        },
        {
            "VOL_ID": "11",
            "VOL_NO": "VOLUME - 9",
            "VOL_TITLE": "ELECTRICALS"
        }
    ]
    
    for i in data:
        vol_no = i["VOL_NO"]
        vol_title = i["VOL_TITLE"]
        RSNVolume.objects.update_or_create(volume_no=vol_no, defaults={"volume_title": vol_title})
        

def create_rsn_group():
    data = [
        {
        "VOL_NO": "VOLUME - 1",
        "GROUP_ID": "6",
        "GROUP_NAME": ""
        },
        {
        "VOL_NO": "VOLUME - 6",
        "GROUP_ID": "48",
        "GROUP_NAME": ""
        },
        {
        "VOL_NO": "VOLUME - 8",
        "GROUP_ID": "62",
        "GROUP_NAME": "Accumulators"
        },
        {
        "VOL_NO": "VOLUME - 4",
        "GROUP_ID": "27",
        "GROUP_NAME": "Antifriction Bearings and Accessories, Plummer blocks"
        },
        {
        "VOL_NO": "VOLUME - 1a",
        "GROUP_ID": "12",
        "GROUP_NAME": "Bevel Gears"
        },
        {
        "VOL_NO": "VOLUME - 7",
        "GROUP_ID": "54",
        "GROUP_NAME": "Bottom Block, hood, hooks, Laminated hooks."
        },
        {
        "VOL_NO": "VOLUME - 8",
        "GROUP_ID": "65",
        "GROUP_NAME": "Centralised Lubrication Pumps, Hand Lubrication Pumps, Centralised Oil Pumps, Distributors"
        },
        {
        "VOL_NO": "VOLUME - 1",
        "GROUP_ID": "9",
        "GROUP_NAME": "Civil and structurals"
        },
        {
        "VOL_NO": "VOLUME - 1",
        "GROUP_ID": "7",
        "GROUP_NAME": "Compression soring, tension, torsion springs & disc soring."
        },
        {
        "VOL_NO": "VOLUME - 1",
        "GROUP_ID": "3",
        "GROUP_NAME": "Construction"
        },
        {
        "VOL_NO": "VOLUME - 5",
        "GROUP_ID": "37",
        "GROUP_NAME": "Counter sunk head screws & screws"
        },
        {
        "VOL_NO": "VOLUME - 8",
        "GROUP_ID": "60",
        "GROUP_NAME": "Cylinders"
        },
        {
        "VOL_NO": "VOLUME - 1",
        "GROUP_ID": "2",
        "GROUP_NAME": "Drawing Dimensioning Drg. Practice"
        },
        {
        "VOL_NO": "VOLUME - 4",
        "GROUP_ID": "31",
        "GROUP_NAME": "Electric & Oxygen Acetylene Weldings"
        },
        {
        "VOL_NO": "VOLUME - 9",
        "GROUP_ID": "69",
        "GROUP_NAME": "Electrical Equipments for crane"
        },
        {
        "VOL_NO": "VOLUME - 9",
        "GROUP_ID": "67",
        "GROUP_NAME": "Electrical Machines"
        },
        {
        "VOL_NO": "VOLUME - 7",
        "GROUP_ID": "55",
        "GROUP_NAME": "Fastening Devices"
        },
        {
        "VOL_NO": "VOLUME - 2",
        "GROUP_ID": "20",
        "GROUP_NAME": "Ferrous Metals"
        },
        {
        "VOL_NO": "VOLUME - 1",
        "GROUP_ID": "4",
        "GROUP_NAME": "Fits and Tolerances"
        },
        {
        "VOL_NO": "VOLUME - 1",
        "GROUP_ID": "8",
        "GROUP_NAME": "Flange coupling with slit push & taper key-way."
        },
        {
        "VOL_NO": "VOLUME - 6",
        "GROUP_ID": "46",
        "GROUP_NAME": "Flange seals"
        },
        {
        "VOL_NO": "VOLUME - 5",
        "GROUP_ID": "39",
        "GROUP_NAME": "Foundation bolts. Studs."
        },
        {
        "VOL_NO": "VOLUME - 5",
        "GROUP_ID": "35",
        "GROUP_NAME": "Fundamentals"
        },
        {
        "VOL_NO": "VOLUME - 1a",
        "GROUP_ID": "14",
        "GROUP_NAME": "Gear Boxes"
        },
        {
        "VOL_NO": "VOLUME - 1a",
        "GROUP_ID": "10",
        "GROUP_NAME": "Gear General"
        },
        {
        "VOL_NO": "VOLUME - 1a",
        "GROUP_ID": "13",
        "GROUP_NAME": "Gears Worm And Worm Wheel"
        },
        {
        "VOL_NO": "VOLUME - 9",
        "GROUP_ID": "66",
        "GROUP_NAME": "General"
        },
        {
        "VOL_NO": "VOLUME - 2",
        "GROUP_ID": "15",
        "GROUP_NAME": "General guide- designation, testing"
        },
        {
        "VOL_NO": "VOLUME - 2",
        "GROUP_ID": "16",
        "GROUP_NAME": "General structural steel Hot & Cold Rolled Sheets"
        },
        {
        "VOL_NO": "VOLUME - 2",
        "GROUP_ID": "17",
        "GROUP_NAME": "General structural steels : Rounds, flats"
        },
        {
        "VOL_NO": "VOLUME - 2",
        "GROUP_ID": "18",
        "GROUP_NAME": "General structural steels, Equal and Un-equal angles, tee, beems, channels."
        },
        {
        "VOL_NO": "VOLUME - 2",
        "GROUP_ID": "19",
        "GROUP_NAME": "General structural steels, sheared and un-sheared heavy plates"
        },
        {
        "VOL_NO": "VOLUME - 4",
        "GROUP_ID": "33",
        "GROUP_NAME": "Handles"
        },
        {
        "VOL_NO": "VOLUME - 8",
        "GROUP_ID": "61",
        "GROUP_NAME": "Handling Equipment"
        },
        {
        "VOL_NO": "VOLUME - 5",
        "GROUP_ID": "36",
        "GROUP_NAME": "Hexagonal screws and bolts"
        },
        {
        "VOL_NO": "VOLUME - 6",
        "GROUP_ID": "47",
        "GROUP_NAME": "Hose pipes"
        },
        {
        "VOL_NO": "VOLUME - 8",
        "GROUP_ID": "59",
        "GROUP_NAME": "Hydraulic Guide Lines, Specifications, Ordering Instructions."
        },
        {
        "VOL_NO": "VOLUME - 9",
        "GROUP_ID": "68",
        "GROUP_NAME": "Hydraulic Thrustor (Eldro)"
        },
        {
        "VOL_NO": "VOLUME - 4",
        "GROUP_ID": "28",
        "GROUP_NAME": "Journal Bearing Bushes"
        },
        {
        "VOL_NO": "VOLUME - 4",
        "GROUP_ID": "30",
        "GROUP_NAME": "Keys"
        },
        {
        "VOL_NO": "VOLUME - 7",
        "GROUP_ID": "56",
        "GROUP_NAME": "Lifting Tools & Tackles"
        },
        {
        "VOL_NO": "VOLUME - 9",
        "GROUP_ID": "71",
        "GROUP_NAME": "Limint switches"
        },
        {
        "VOL_NO": "VOLUME - 9",
        "GROUP_ID": "64",
        "GROUP_NAME": "Lubricants, Oil and Greases."
        },
        {
        "VOL_NO": "VOLUME - 8",
        "GROUP_ID": "63",
        "GROUP_NAME": "Lubrication Guide lines, Specifications, Ordering Instructions."
        },
        {
        "VOL_NO": "VOLUME - 1",
        "GROUP_ID": "5",
        "GROUP_NAME": "Metric screw threads"
        },
        {
        "VOL_NO": "VOLUME - 7",
        "GROUP_ID": "51",
        "GROUP_NAME": "Motor, rigid drums, safety coupling Brackes, Air Appliances"
        },
        {
        "VOL_NO": "VOLUME - 2",
        "GROUP_ID": "21",
        "GROUP_NAME": "Non-Ferrous Metal"
        },
        {
        "VOL_NO": "VOLUME - 2",
        "GROUP_ID": "22",
        "GROUP_NAME": "Non-Metallic Materials"
        },
        {
        "VOL_NO": "VOLUME - 5",
        "GROUP_ID": "40",
        "GROUP_NAME": "Nut"
        },
        {
        "VOL_NO": "VOLUME - 5",
        "GROUP_ID": "41",
        "GROUP_NAME": "Parallel pins"
        },
        {
        "VOL_NO": "VOLUME - 6",
        "GROUP_ID": "44",
        "GROUP_NAME": "Pipes"
        },
        {
        "VOL_NO": "VOLUME - 4",
        "GROUP_ID": "32",
        "GROUP_NAME": "Portable Hand Tools"
        },
        {
        "VOL_NO": "VOLUME - 4",
        "GROUP_ID": "34",
        "GROUP_NAME": "Power transmission belt & pulleys"
        },
        {
        "VOL_NO": "VOLUME - 6",
        "GROUP_ID": "49",
        "GROUP_NAME": "Pressure and Vaccum guages"
        },
        {
        "VOL_NO": "VOLUME - 9",
        "GROUP_ID": "70",
        "GROUP_NAME": "Resistors for carnes"
        },
        {
        "VOL_NO": "VOLUME - 7",
        "GROUP_ID": "53",
        "GROUP_NAME": "Ropes, Rope Pulleys, Rope drums, Crooved Profiles"
        },
        {
        "VOL_NO": "VOLUME - 5",
        "GROUP_ID": "38",
        "GROUP_NAME": "Screws (Handling Type)"
        },
        {
        "VOL_NO": "VOLUME - 4",
        "GROUP_ID": "29",
        "GROUP_NAME": "Seals"
        },
        {
        "VOL_NO": "VOLUME - 3",
        "GROUP_ID": "24",
        "GROUP_NAME": "Sork shop practices & equipments Portable  Elect. Tool"
        },
        {
        "VOL_NO": "VOLUME - 1a",
        "GROUP_ID": "11",
        "GROUP_NAME": "Spur Gears"
        },
        {
        "VOL_NO": "VOLUME - 1",
        "GROUP_ID": "1",
        "GROUP_NAME": "Standard sizes for drawings & Title Blocks"
        },
        {
        "VOL_NO": "VOLUME - 6",
        "GROUP_ID": "45",
        "GROUP_NAME": "Steel tubes"
        },
        {
        "VOL_NO": "VOLUME - 2",
        "GROUP_ID": "23",
        "GROUP_NAME": "Structural"
        },
        {
        "VOL_NO": "VOLUME - 5",
        "GROUP_ID": "43",
        "GROUP_NAME": "Tab washers"
        },
        {
        "VOL_NO": "VOLUME - 7",
        "GROUP_ID": "52",
        "GROUP_NAME": "Track wheels & Transmission gears, rails"
        },
        {
        "VOL_NO": "VOLUME -7a",
        "GROUP_ID": "58",
        "GROUP_NAME": "Transport equipment Conveyors, buckets, Bogies"
        },
        {
        "VOL_NO": "VOLUME -7a",
        "GROUP_ID": "57",
        "GROUP_NAME": "Transport equipment Wheel barrows, Hand-carts. Fork Lift, Trucks, Electric trucks."
        },
        {
        "VOL_NO": "VOLUME - 6",
        "GROUP_ID": "50",
        "GROUP_NAME": "Valves"
        },
        {
        "VOL_NO": "VOLUME - 4",
        "GROUP_ID": "42",
        "GROUP_NAME": "Washers"
        },
        {
        "VOL_NO": "VOLUME - 3",
        "GROUP_ID": "25",
        "GROUP_NAME": "Workshop practice & Equipments Tools for Machining"
        },
        {
        "VOL_NO": "VOLUME - 3",
        "GROUP_ID": "26",
        "GROUP_NAME": "Workshop Practices & Equipments Tools"
        }
        ]
    
    for i in data:
        vol_no = i["VOL_NO"]
        group_name = i["GROUP_NAME"]
        group_id = i["GROUP_ID"]
        volume = RSNVolume.objects.get(volume_no=vol_no)
        RSNGroup.objects.update_or_create(rsn_volume = volume, group_id=group_id, defaults={"name": group_name})


def fix_drawing_file_path(folder_path, drawing_type):
    try:
        total_created = 0
        drawings = Drawing.objects.filter(is_file_present=False, drawing_type=drawing_type)
        for drawing in drawings:
            is_file_exist = True
            if drawing.no_of_sheet == 1:
                if drawing.drawing_file_type == "PDF":
                    file_name_list = [f"{drawing_type}-{drawing.drawing_number}.pdf", f"{drawing_type}-{drawing.drawing_number}.PDF"]
                else:
                    file_name_list = [f"{drawing_type}-{drawing.drawing_number}.tif", 
                                    f"{drawing_type}-{drawing.drawing_number}.TIF",
                                    f"{drawing_type}-{drawing.drawing_number}.tiff",
                                    f"{drawing_type}-{drawing.drawing_number}.TIFF"
                                    ]
                for file_name in file_name_list:
                    file_path = os.path.join(folder_path, file_name)
                    if os.path.isfile(file_path):
                        is_file_exist = True
                        dwg_file = None
                        if drawing.is_dwg_file_present:
                            dwg_file_list = [f"{drawing_type}-{drawing.drawing_number}.dwg", f"{drawing_type}-{drawing.drawing_number}.DWG"]
                            for dwg_name in dwg_file_list:
                                dwg_file_path = os.path.join(folder_path, dwg_name)
                                if os.path.isfile(dwg_file_path):
                                    dwg_file = dwg_file_path
                                    break
                        d_file_name,  extension = os.path.splitext(file_name)
                        if not DrawingFile.objects.filter(drawing=drawing, file_name=d_file_name).exists():
                            DrawingFile.objects.create(drawing=drawing, file=file_path, dwg_file=dwg_file, file_name=d_file_name)
                            drawing.is_file_present = True
                            drawing.is_approved = True
                            drawing.save()
                            total_created += 1
                        break
                    else:
                        is_file_exist = False

                if not is_file_exist:
                    print(f"File Not Found: {file_name} | Drawing Number: {drawing.drawing_number}")
            else:
                # Handle multiple sheets
                for sheet_number in range(1, drawing.no_of_sheet + 1):
                    if drawing.drawing_file_type == "PDF":
                        file_name_list = [
                            f"{drawing_type}-{drawing.drawing_number}SH{sheet_number}.pdf", 
                            f"{drawing_type}-{drawing.drawing_number}SH{sheet_number}.PDF",
                        ]
                    else:
                        file_name_list = [
                            f"{drawing_type}-{drawing.drawing_number}SH{sheet_number}.tif", 
                            f"{drawing_type}-{drawing.drawing_number}SH{sheet_number}.TIF",
                            f"{drawing_type}-{drawing.drawing_number}SH{sheet_number}.tiff",
                            f"{drawing_type}-{drawing.drawing_number}SH{sheet_number}.TIFF"
                        ]

                    for file_name in file_name_list:
                        file_path = os.path.join(folder_path, file_name)
                        if os.path.isfile(file_path):
                            is_file_exist = True
                            dwg_file = None
                            if drawing.is_dwg_file_present:
                                for sheet_number in range(1, drawing.no_of_sheet + 1):
                                    dwg_file_list = [
                                        f"{drawing_type}-{drawing.drawing_number}SH{sheet_number}.dwg", 
                                        f"{drawing_type}-{drawing.drawing_number}SH{sheet_number}.dwg",
                                    ]
                                for dwg_name in dwg_file_list:
                                    dwg_file_path = os.path.join(folder_path, dwg_name)
                                    if os.path.isfile(dwg_file_path):
                                        dwg_file = dwg_file_path
                                        break
                            d_file_name,  extension = os.path.splitext(file_name)
                            if not DrawingFile.objects.filter(drawing=drawing, file_name=d_file_name).exists():
                                DrawingFile.objects.create(drawing=drawing, file=file_path, dwg_file=dwg_file, file_name=d_file_name)
                                if drawing.no_of_sheet == drawing.files.count():
                                    drawing.is_file_present = True
                                    drawing.is_approved = True
                                    drawing.save()
                                    total_created += 1
                            break
                        else:
                            is_file_exist = False
                    if not is_file_exist:
                        print(f"File Not Found: {file_name} | Drawing Number: {drawing.drawing_number}")
    except Exception as e:
        print("ERROR", e)
        Syserror(e)

    print("Total applied", total_created)

def fix_pdr_drawing_file_path(folder_path, drawing_type, json_path):
    new_not_found_drawings = []
    try:
        total_created = 0
        not_found_drawings = []
        if Path(json_path).is_file():
            with open(json_path, 'r') as f:
                data = json.load(f)
                not_found_drawings = data.get('drawing_number', [])
        drawings = Drawing.objects.filter(is_file_present=False, drawing_type=drawing_type)
        drawings = drawings.exclude(drawing_number__in=not_found_drawings)[:50000]
        for drawing in drawings:
            is_file_exist = True
            if drawing.no_of_sheet == 1:
                if drawing.drawing_file_type == "PDF":
                    file_name_list = [f"{drawing_type}-{drawing.drawing_number}.pdf", f"{drawing_type}-{drawing.drawing_number}.PDF"]
                else:
                    file_name_list = [f"{drawing_type}-{drawing.drawing_number}.tif", 
                                    f"{drawing_type}-{drawing.drawing_number}.TIF",
                                    f"{drawing_type}-{drawing.drawing_number}.tiff",
                                    f"{drawing_type}-{drawing.drawing_number}.TIFF"
                                    ]
                for file_name in file_name_list:
                    file_path = os.path.join(folder_path, file_name)
                    if os.path.isfile(file_path):
                        is_file_exist = True
                        dwg_file = None
                        if drawing.is_dwg_file_present:
                            dwg_file_list = [f"{drawing_type}-{drawing.drawing_number}.dwg", f"{drawing_type}-{drawing.drawing_number}.DWG"]
                            for dwg_name in dwg_file_list:
                                dwg_file_path = os.path.join(folder_path, dwg_name)
                                if os.path.isfile(dwg_file_path):
                                    dwg_file = dwg_file_path
                                    break
                        d_file_name,  extension = os.path.splitext(file_name)
                        if not DrawingFile.objects.filter(drawing=drawing, file_name=d_file_name).exists():
                            DrawingFile.objects.create(drawing=drawing, file=file_path, dwg_file=dwg_file, file_name=d_file_name)
                            drawing.is_file_present = True
                            drawing.is_approved = True
                            drawing.save()
                            total_created += 1
                        break
                    else:
                        is_file_exist = False

                if not is_file_exist:
                    new_not_found_drawings.append(drawing.drawing_number)
                    print(f"File Not Found: {file_name} | Drawing Number: {drawing.drawing_number}")
            else:
                # Handle multiple sheets
                for sheet_number in range(1, drawing.no_of_sheet + 1):
                    if drawing.drawing_file_type == "PDF":
                        file_name_list = [
                            f"{drawing_type}-{drawing.drawing_number}SH{sheet_number}.pdf", 
                            f"{drawing_type}-{drawing.drawing_number}SH{sheet_number}.PDF",
                        ]
                    else:
                        file_name_list = [
                            f"{drawing_type}-{drawing.drawing_number}SH{sheet_number}.tif", 
                            f"{drawing_type}-{drawing.drawing_number}SH{sheet_number}.TIF",
                            f"{drawing_type}-{drawing.drawing_number}SH{sheet_number}.tiff",
                            f"{drawing_type}-{drawing.drawing_number}SH{sheet_number}.TIFF"
                        ]

                    for file_name in file_name_list:
                        file_path = os.path.join(folder_path, file_name)
                        if os.path.isfile(file_path):
                            is_file_exist = True
                            dwg_file = None
                            if drawing.is_dwg_file_present:
                                for sheet_number in range(1, drawing.no_of_sheet + 1):
                                    dwg_file_list = [
                                        f"{drawing_type}-{drawing.drawing_number}SH{sheet_number}.dwg", 
                                        f"{drawing_type}-{drawing.drawing_number}SH{sheet_number}.dwg",
                                    ]
                                for dwg_name in dwg_file_list:
                                    dwg_file_path = os.path.join(folder_path, dwg_name)
                                    if os.path.isfile(dwg_file_path):
                                        dwg_file = dwg_file_path
                                        break
                            d_file_name,  extension = os.path.splitext(file_name)
                            if not DrawingFile.objects.filter(drawing=drawing, file_name=d_file_name).exists():
                                DrawingFile.objects.create(drawing=drawing, file=file_path, dwg_file=dwg_file, file_name=d_file_name)
                                if drawing.no_of_sheet == drawing.files.count():
                                    drawing.is_file_present = True
                                    drawing.is_approved = True
                                    drawing.save()
                                    total_created += 1
                            break
                        else:
                            is_file_exist = False
                    if not is_file_exist:
                        print(f"File Not Found: {file_name} | Drawing Number: {drawing.drawing_number}")
    except Exception as e:
        Syserror(e)
    if new_not_found_drawings:
        not_found_drawings.extend(new_not_found_drawings)
        with open(json_path, 'w') as f:
            json.dump({"drawing_number":not_found_drawings}, f)
    print("Total applied", total_created)

def remove_unwanted_drawing_file(folder_path, drawing_type):
    total_created = 0
    for filename  in os.scandir(folder_path):
        if not filename.is_file():
            continue
        file = os.path.basename(filename.path)
        name, extension = get_file_name_and_extension(file)
        file_drawing_type, drawing_number = extract_drawing_type_number(name)
        if file_drawing_type != drawing_type:
            print(f"Invalid Drawing Type. FILE {file}")
            continue
        if extension not in  ["PDF", "TIF", "TIFF", "DWG"]:
            print(f"Invalid Extension. FILE {file}")
            continue
        if extension == "PDF":
            if not Drawing.objects.filter(drawing_number = drawing_number, drawing_type = drawing_type, drawing_file_type="PDF").exists():
                os.remove(filename.path)
                total_created += 1
        elif extension in ["TIFF", "TIF"]:
            if not Drawing.objects.filter(drawing_number = drawing_number, drawing_type = drawing_type, drawing_file_type="TIF").exists():
                os.remove(filename.path)
                total_created += 1
        elif extension == "DWG":
            if not Drawing.objects.filter(drawing_number = drawing_number, drawing_type = drawing_type, is_dwg_file_present = True).exists():
                os.remove(filename.path)
                total_created += 1
        else:
            os.remove(filename.path)
            total_created += 1
    print("Total removed", total_created)

def verify_files_exist(first_dir, second_dir):
    first_files = os.listdir(first_dir)
    second_files = os.listdir(second_dir)
    missing_files = []

    for file_name in first_files:
        if file_name not in second_files:
            missing_files.append(file_name)

    # Print the list of missing files
    if missing_files:
        print("The following files are missing in the second directory:")
        for file_name in missing_files:
            print(file_name)
    else:
        print("All files from the first directory exist in the second directory.")

def countpath(dirpath):
    count = 0
    for path in os.scandir(dirpath):
        if path.is_file():
            count += 1
    return count

def make_quniue_file_name(file_name, base_dir):
    original_path = os.path.join(base_dir, file_name)
    counter = 1
    while os.path.exists(original_path):
        name, extension = os.path.splitext(file_name)
        new_file_name = f"{name}{counter}{extension}"
        original_path = os.path.join(base_dir, new_file_name)
        counter += 1
    return original_path

def uploadStandard(directory_path, json_path):
    import json
    import os
    import shutil
    from django.db import transaction
    from AuthApp.models import User
    from StandardApp.models import Standard, StandardLog, RSNGroup, IPSSTitle
    try:
        with open(json_path, 'r', encoding='utf-8') as data_file:
            data_list  = json.load(data_file)
            new_data_list = []
            error_data_set = []
            for index, data in enumerate(data_list['data'], start=2):
                standard_type = data.get("standard_type", "BIS")
                standard_no = data.get("standard_number", None) or None
                part_no = data.get("part_number", None) or None
                section_no = data.get("section_number", None) or None
                document_year = data.get("document_year", None) or None
                division = data.get("division", None) or None
                division_code = data.get("division_code", None) or None
                committee_code = data.get("committee_code", None) or None
                committee_title = data.get("committee_title", None) or None
                description = data.get("description", None) or None
                group = data.get("group_id", None) or None
                no_of_sheet = data.get("no_of_sheet", None) or None
                title_id = data.get("title_id", None) or None
                file_availability = data.get("file_availability", "NO") == "YES"
                file = data.get("file", None) or None
                required_field = [standard_type,standard_no]

                if not all(required_field):
                    error_data_set.append({"row": index, "message": "Required mandatory fields."})
                    continue
                
                if standard_type == "BIS":
                    group = None
                    no_of_sheet = None
                    title_id = None
                    file_availability = None
                elif standard_type in ["ASTM","AWWA","BRITISH","DIN(GERMAN)","GOST(RUSSIAN)","IEC","ISO","IRST","API","PSN"]:
                    division = None
                    division_code = None
                    committee_code = None
                    committee_title = None
                    group = None
                    no_of_sheet = None
                    title_id = None
                    file_availability = None
                elif standard_type == "RSN":
                    part_no = None
                    section_no = None
                    document_year = None
                    title_id = None
                    committee_code = None
                    committee_title = None
                    file_availability = None
                    if not no_of_sheet or not str(no_of_sheet).isdigit() or int(no_of_sheet) < 1:
                        error_data_set.append(
                            {"row": index, "message": "Invalid number of sheet."}
                        )
                        continue

                    if group:
                            if group_exist := RSNGroup.objects.filter(group_id__icontains = group):
                                group = group_exist.first()
                            else:
                                error_data_set.append(
                                    {"row": index, "message": "Group doesn't exist."}
                                )
                                continue
                    else:
                        group = None 

                elif standard_type == "IPSS":
                    division = None
                    division_code = None
                    committee_code = None
                    committee_title = None
                    group = None
                    no_of_sheet = None
                    part_no = None
                    section_no = None
                    document_year = None
                    if title_id:
                        if title_exist := IPSSTitle.objects.filter(title_id__icontains = title_id):
                            title_id = title_exist.first()
                        else:
                            error_data_set.append(
                                {"row": index, "message": "Title doesn't exist."}
                            )
                            continue
                    else:
                        title_id = None
                else:
                    error_data_set.append(
                        {"row": index, "message": "Invalid standard type."}
                    )
                if standard_type == "IPSS" and not file_availability:
                    file = None
                elif standard_type == "IPSS" and file_availability and not file:
                    error_data_set.append({"row": index, "message": "Required file ."})
                    continue
                else:
                    if file:
                        file_path = os.path.join(directory_path, file)
                        if os.path.isfile(file_path):
                            file = file_path
                        else:
                            error_data_set.append(
                                {"row": index, "message": "File didn't match."}
                            )
                            continue
                
                if not error_data_set:
                    new_data_list.append({
                        "standard_no": standard_no,
                        "standard_type": standard_type,
                        "part_no": part_no,
                        "section_no": section_no,
                        "document_year": document_year,
                        "division": division,
                        "division_code": division_code,
                        "committee_code": committee_code,
                        "committee_title": committee_title,
                        "description": description,
                        "group": group,
                        "no_of_sheet": no_of_sheet,
                        "title_id": title_id,
                        "file_availability": file_availability,
                        "file": file
                    })
            if not error_data_set:
                user = User.objects.filter(is_superuser =True).first()
                with transaction.atomic():
                    for data in new_data_list:
                        standard_no = data.get("standard_no")
                        standard_type = data.get("standard_type")
                        part_no = data.get("part_no")
                        section_no = data.get("section_no")
                        document_year = data.get("document_year")
                        division = data.get("division")
                        division_code = data.get("division_code")
                        committee_code = data.get("committee_code")
                        committee_title = data.get("committee_title")
                        description = data.get("description")
                        group = data.get("group")
                        no_of_sheet = data.get("no_of_sheet")
                        title_id = data.get("title_id")
                        file_availability = data.get("file_availability")
                        file = data.get("file")
                        if file:
                            file_name = os.path.basename(file)
                            standard_media_path = "/home/designadmin/odms/media/standard"
                            new_file = make_quniue_file_name(standard_media_path, file_name)
                            shutil.copy2(file, new_file)
                            file = new_file
                        if group:
                            volume = group.rsn_volume
                        else:
                            volume = None
                                                    
                        instance = Standard.objects.create(
                            standard_type = standard_type,
                            standard_no = standard_no,
                            part_no = part_no,
                            section_no = section_no,
                            document_year = document_year,
                            division = division,
                            division_code = division_code,
                            committee_code = committee_code,
                            committee_title = committee_title,
                            description = description,
                            group = group,
                            rsn_volume = volume,
                            no_of_sheet = no_of_sheet,
                            title = title_id,
                            file_availability = file_availability if standard_type == "IPSS" else None,
                            upload_file = file,
                            is_approved = True
                        )
                        StandardLog.objects.create(
                            user = user,
                            standard = instance,
                            status = "Add Standard",
                            message = "Standard added from bulk upload.",
                            details = f"Add standard data from bulk upload excel file."
                        )
            if error_data_set:
                for err in error_data_set:
                    print(err)
            else:
                print("NO ERRROR")
    except Exception as e:
        Syserror(e)

def copy_files(file_names, source_directory, copy_directory):
    import os
    import shutil
    if not os.path.exists(copy_directory):
        os.makedirs(copy_directory)
    copied_files = set()
    for root, _, files in os.walk(source_directory):
        for file_name in files:
            if file_name in file_names and file_name not in copied_files:
                source_path = os.path.join(root, file_name)
                destination_path = os.path.join(copy_directory, file_name)
                if not os.path.exists(destination_path):
                    shutil.copy2(source_path, destination_path)
                    copied_files.add(file_name)
                    print(f"Copied: {source_path} to {destination_path}")
                else:
                    print(f"Duplicate file not copied: {file_name}")

# Example usage
# file_names = ["is8782.pdf", "PDR-1122.pdf", "yuetufhwg.pdf", "tryhbm,ncss.pdf", "hjkslkwju.pdf", "mnn,jdlkelkkejlk.pdf", 
# "kjhdhejke7656.pdf",",mnekjelkk.pdf","ytyte7676.pdf","kjjmnmn7.pdf","98hjjhg.pdf","776hjhjshbs.pdf","shwghjgwhge.pdf",
# "7876jhhgjhjg.pdf","hghghgw.pdf"]
# source_directory = "F:\BIS(NOT TO BE DELETED)\BIS1"
# copy_directory = "F:\BIS(NOT TO BE DELETED)\TEMPSERVERBIS"
# copy_files(file_names, source_directory, copy_directory)



# nf = []
# for file in file_names:
#     fp = os.path.join(folder_path, file)
#     if not os.path.isfile(fp):
#         print(fp)
#         nf.append(file)

def update_drawing_numeric_numbers():
    drawings = Drawing.objects.all()
    for drawing in drawings:
        drawing.drawing_number_numeric = int(''.join(filter(str.isdigit, drawing.drawing_number)) or 0)
        drawing.save()