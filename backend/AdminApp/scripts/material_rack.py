from AdminApp.models import *
from AuthApp.models import *
from datetime import datetime, timedelta
from django.db import transaction
import random
from AdminApp.utils import encrypt_user_secret_token


def createRack(data=[]):
    sampledata = [
    "Zone-1 Rack-01", "Zone-1 Rack-02", "Zone-1 Rack-03",
    "Zone-2 Rack-01", "Zone-2 Rack-02", "Zone-2 Rack-03",
    "Zone-3 Rack-01", "Zone-3 Rack-02", "Zone-3 Rack-03",
    "Zone-4 Rack-01", "Zone-4 Rack-02", "Zone-4 Rack-03",
    "Zone-5 Rack-01", "Zone-5 Rack-02", "Zone-5 Rack-03",
    "Overflow Rack-01", "Overflow Rack-02", "Overflow Rack-03", "Overflow Rack-04"
    ]

    if data == []:
        data = sampledata

    rack_list = []
    for i in data:
        with transaction.atomic():
            barcode = Barcodes.objects.create(is_product_type=False, status="Used")
            rack = Racks.objects.create(rack_no=i, barcode=barcode)
            rack_list.append(
                {"id": rack.id, "rack_no": rack.rack_no, "barcoee": i["barcode"]}
            )
    return rack_list


def createProduct(data_list):
    
    sampledata = [
        {
            "name": "High Carbon Ferrochrome",
            "material_category": "Alloying Elements",
            "ucs_code": "UCS123456789057",
            "min_threshold": 200,
            "max_threshold": 800,
            "price": 25000,
            "unit": "KG",
            "ved_category": "Vital",
            "lead_time": 5,
            "description": "Ferrochrome used in steelmaking",
            "material_type_unit": "Single Item",
            "description_sap": "High Carbon Ferrochrome",
            "is_perishable":"No"
        },
        {
            "name": "Dolomite Bricks",
            "material_category": "Refractories",
            "ucs_code": "UCS123456789058",
            "min_threshold": 1000,
            "max_threshold": 5000,
            "price": 300,
            "unit": "Number",
            "ved_category": "Essential",
            "lead_time": 7,
            "description": "Refractory bricks for furnace lining",
            "material_type_unit": "Multiple Item",
            "description_sap": "Dolomite Bricks",
            "is_perishable":"No"
        },
        {
            "name": "Diesel Fuel",
            "material_category": "Fuels",
            "ucs_code": "UCS123456789059",
            "min_threshold": 10000,
            "max_threshold": 50000,
            "price": 90,
            "unit": "Liter",
            "ved_category": "Vital",
            "lead_time": 3,
            "description": "Fuel for plant machinery",
            "material_type_unit": "Single Item",
            "description_sap": "Diesel Fuel",
            "is_perishable": "No",
        },
        {
            "name": "Hydraulic Oil",
            "material_category": "Lubricants and Coolants",
            "ucs_code": "UCS123456789060",
            "min_threshold": 500,
            "max_threshold": 2500,
            "price": 400,
            "unit": "Liter",
            "ved_category": "Essential",
            "lead_time": 2,  # in days
            "description": "Lubricant for hydraulic systems",
            "material_type_unit": "Single Item",
            "description_sap": "Hydraulic Oil",
            "is_perishable": "No",
        },
        {
            "name": "Safety Gloves",
            "material_category": "Personal Protective Equipment",
            "ucs_code": "UCS123456789061",
            "min_threshold": 1000,
            "max_threshold": 5000,
            "price": 50,
            "unit": "Number",
            "ved_category": "Vital",
            "lead_time": 1,  # in days
            "description": "Gloves for worker safety",
            "material_type_unit": "Multiple Item",
            "description_sap": "Safety Gloves",
            "is_perishable": "No",
        },
        {
            "name": "Steel Billets",
            "material_category": "Raw Materials",
            "ucs_code": "UCS123456789062",
            "min_threshold": 5000,
            "max_threshold": 20000,
            "price": 45000,
            "unit": "KG",
            "ved_category": "Vital",
            "lead_time": 10,  # in days
            "description": "Primary raw material for rolling",
            "material_type_unit": "Single Item",
            "description_sap": "Steel Billets",
            "is_perishable": "No",
        },
        {
            "name": "Blast Furnace Slag Cement",
            "material_category": "Construction Materials",
            "ucs_code": "UCS123456789063",
            "min_threshold": 1000,
            "max_threshold": 5000,
            "price": 250,
            "unit": "KG",
            "ved_category": "Essential",
            "lead_time": 5,  # in days
            "description": "Cement for construction and repair",
            "material_type_unit": "Multiple Item",
            "description_sap": "Blast Furnace Slag Cement",
            "is_perishable": "Yes",
        },
        {
            "name": "Sulfuric Acid",
            "material_category": "Chemicals",
            "ucs_code": "UCS123456789064",
            "min_threshold": 200,
            "max_threshold": 1000,
            "price": 150,
            "unit": "Liter",
            "ved_category": "Desirable",
            "lead_time": 4,  # in days
            "description": "Acid used in pickling processes",
            "material_type_unit": "Single Item",
            "description_sap": "Sulfuric Acid",
            "is_perishable": "Yes",
        },
        {
            "name": "Silicon Manganese",
            "material_category": "Alloying Elements",
            "ucs_code": "UCS123456789065",
            "min_threshold": 500,
            "max_threshold": 2000,
            "price": 60000,
            "unit": "KG",
            "ved_category": "Vital",
            "lead_time": 6,  # in days
            "description": "Used in steelmaking for deoxidation",
            "material_type_unit": "Single Item",
            "description_sap": "Silicon Manganese",
            "is_perishable": "No",
        },
        {
            "name": "Graphite Electrodes",
            "material_category": "Spare Parts",
            "ucs_code": "UCS123456789066",
            "min_threshold": 50,
            "max_threshold": 200,
            "price": 70000,
            "unit": "Number",
            "ved_category": "Vital",
            "lead_time": 15,  # in days
            "description": "Electrodes used in electric arc furnaces",
            "material_type_unit": "Single Item",
            "description_sap": "Graphite Electrodes",
            "is_perishable": "No",
        },
        {
            "name": "Fireclay Mortar",
            "material_category": "Refractories",
            "ucs_code": "UCS123456789067",
            "min_threshold": 500,
            "max_threshold": 2000,
            "price": 150,
            "unit": "KG",
            "ved_category": "Essential",
            "lead_time": 4,  # in days
            "description": "Mortar for brickwork in furnaces",
            "material_type_unit": "Single Item",
            "description_sap": "Fireclay Mortar",
            "is_perishable": "No",
        },
        {
            "name": "Industrial Oxygen Cylinders",
            "material_category": "Chemicals",
            "ucs_code": "UCS123456789068",
            "min_threshold": 100,
            "max_threshold": 500,
            "price": 3000,
            "unit": "Number",
            "ved_category": "Vital",
            "lead_time": 2,  # in days
            "description": "Oxygen for cutting and welding",
            "material_type_unit": "Single Item",
            "description_sap": "Industrial Oxygen Cylinders",
            "is_perishable": "No",
        },
        {
            "name": "Graphite Grease",
            "material_category": "Lubricants and Coolants",
            "ucs_code": "UCS123456789069",
            "min_threshold": 300,
            "max_threshold": 1500,
            "price": 250,
            "unit": "KG",
            "ved_category": "Essential",
            "lead_time": 3,  # in days
            "description": "Grease for high-temperature applications",
            "material_type_unit": "Single Item",
            "description_sap": "Graphite Grease",
            "is_perishable": "Yes",
        },
        {
            "name": "Aluminum Sheets",
            "material_category": "Raw Materials",
            "ucs_code": "UCS123456789070",
            "min_threshold": 2000,
            "max_threshold": 10000,
            "price": 150000,
            "unit": "KG",
            "ved_category": "Vital",
            "lead_time": 8,  # in days
            "description": "Sheets for fabrication and repair",
            "material_type_unit": "Single Item",
            "description_sap": "Aluminum Sheets",
            "is_perishable": "No",
        },
        {
            "name": "TMT Bars",
            "material_category": "Construction Materials",
            "ucs_code": "UCS123456789071",
            "min_threshold": 5000,
            "max_threshold": 20000,
            "price": 45000,
            "unit": "KG",
            "ved_category": "Essential",
            "lead_time": 7,  # in days
            "description": "Bars for structural reinforcement",
            "material_type_unit": "Single Item",
            "description_sap": "TMT Bars",
            "is_perishable": "No",
        },
        {
            "name": "Ammonium Nitrate",
            "material_category": "Chemicals",
            "ucs_code": "UCS123456789072",
            "min_threshold": 300,
            "max_threshold": 1200,
            "price": 500,
            "unit": "KG",
            "ved_category": "Desirable",
            "lead_time": 6,  # in days
            "description": "Chemical for explosive production",
            "material_type_unit": "Single Item",
            "description_sap": "Ammonium Nitrate",
            "is_perishable": "No",
        },
        {
            "name": "Steel Reinforcement Wire",
            "material_category": "Raw Materials",
            "ucs_code": "UCS123456789073",
            "min_threshold": 2000,
            "max_threshold": 8000,
            "price": 100000,
            "unit": "KG",
            "ved_category": "Vital",
            "lead_time": 9,  # in days
            "description": "Wire for reinforcing concrete",
            "material_type_unit": "Single Item",
            "description_sap": "Steel Reinforcement Wire",
            "is_perishable": "No",
        },
        {
            "name": "Ball Bearings",
            "material_category": "Spare Parts",
            "ucs_code": "UCS123456789074",
            "min_threshold": 500,
            "max_threshold": 2000,
            "price": 1500,
            "unit": "Number",
            "ved_category": "Essential",
            "lead_time": 2,  # in days
            "description": "Bearings for rolling mills",
            "material_type_unit": "Multiple Item",
            "description_sap": "Ball Bearings",
            "is_perishable": "No",
        },
        {
            "name": "Packaging Straps",
            "material_category": "Packaging Materials",
            "ucs_code": "UCS123456789075",
            "min_threshold": 10000,
            "max_threshold": 40000,
            "price": 5,
            "unit": "Meter",
            "ved_category": "Desirable",
            "lead_time": 3,  # in days
            "description": "Straps for securing bundled products",
            "material_type_unit": "Multiple Item",
            "description_sap": "Packaging Straps",
            "is_perishable": "No",
        },
        {
            "name": "Cooling Water Treatment Chemicals",
            "material_category": "Chemicals",
            "ucs_code": "UCS123456789076",
            "min_threshold": 500,
            "max_threshold": 2000,
            "price": 100,
            "unit": "Liter",
            "ved_category": "Essential",
            "lead_time": 5,  # in days
            "description": "Chemicals for cooling tower water treatment",
            "material_type_unit": "Single Item",
            "description_sap": "Cooling Water Treatment Chemicals",
            "is_perishable": "No",
        },
        {
            "name": "Carbon Electrode Paste",
            "material_category": "Raw Materials",
            "ucs_code": "UCS123456789077",
            "min_threshold": 800,
            "max_threshold": 3000,
            "price": 85000,
            "unit": "KG",
            "ved_category": "Vital",
            "lead_time": 6,  # in days
            "description": "Paste for electrode production",
            "material_type_unit": "Single Item",
            "description_sap": "Carbon Electrode Paste",
            "is_perishable": "Yes",
        },
    ]

    if data_list == []:
        data_list = sampledata

    prodcut_list = []
    for i in data_list:
        unit_get, unit_created = Unit.objects.get_or_create(name=i["unit"])
        cat_get, cat_created = ProductCategory.objects.get_or_create(
            name=i["material_category"]
        )
        prod = Products.objects.create(
            name=i["name"],
            description=i["description"],
            description_sap=i["description_sap"],
            ucs_code=i["ucs_code"],
            min_threshold=i["min_threshold"],
            max_threshold=i["max_threshold"],
            price=i["price"],
            category=cat_get or cat_created,
            unit=unit_get or unit_created,
            is_mutli_type_unit=i["material_type_unit"] == "Multiple Item",
            perishable_product=i["is_perishable"] == "Yes",
            ved_category=i["ved_category"],
            lead_time=i["lead_time"],
        )
        prodcut_list.append({"id": prod.id, "name": i["name"]})
    return prodcut_list


def fix_product():
    Products.objects.update(net_quantity=0)
    Stocks.objects.all().delete()
    Barcodes.objects.filter(is_product_type=True).delete()


def fix_user_secret_token():
    for i in Users.objects.all():
        i.secret_token = encrypt_user_secret_token(i.email)
        i.save()
    print("All user secret token stored properly")


def fix_user_perm():
    from AuthApp.models import Users

    user = Users.objects.all()
    for i in user:
        up = i.user_permission
        up.pop("view_stock_history")
        up["consumption_stockout"] = False
        i.user_permission = up
        i.save()
