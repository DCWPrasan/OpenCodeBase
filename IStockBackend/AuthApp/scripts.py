from AdminApp.models import *
from AuthApp.models import *
from datetime import datetime, timedelta
import random
from AdminApp.utils import encrypt_user_secret_token

def createRack(data):
    """
    sampledata= [
    {"rack_no":"", "barcode":""},
    {"rack_no":"", "barcode":""},
    {"rack_no":"", "barcode":""}
    ]
    """
    rack_list = []
    for i in data:
        if barcode := Barcodes.objects.filter(is_product_type = False, barcode_no = i["barcode"]).first():
            rack = Racks.objects.create(rack_no = i["rack_no"], barcode = barcode)
            rack_list.append({"id":rack.id, "rack_no":rack.rack_no, "barcoee": i["barcode"]})
        else:
            print(f'Barcode Not Found ==> {i["barcode"]}')
    return rack_list

def createProduct(data_list):
    """
    sampledata = [
        {
        "name": "Planning Software License",
        "material_category": "Software",
        "ucs_code": "UCS123456789055",
        "min_threshold": 550,
        "max_threshold": 1550,
        "price": 40000,
        "unit": "Number",
        "description": "License for planning software",
        "is_multi_type_unit": False,
        "description_sap": "Planning Software License"
    },
    {
        "name": "Meeting Room Equipment",
        "material_category": "Office Supplies",
        "ucs_code": "UCS123456789056",
        "min_threshold": 560,
        "max_threshold": 1560,
        "price": 5000,
        "unit": "Number",
        "description": "Equipment for meeting rooms",
        "is_multi_type_unit": False,
        "description_sap": "Meeting Room Equipment"
    }
    ]
    """
    prodcut_list = []
    for i in data_list:
        cat_get, cat_created = ProductCategory.objects.get_or_create(name=i["material_category"])
        prod = Products.objects.create(
            name = i["name"],
            description = i["description"],
            description_sap = i["description_sap"],
            ucs_code = i["ucs_code"],
            min_threshold = i["min_threshold"],
            max_threshold = i["max_threshold"],
            price = i["price"],
            category = cat_get or cat_created,
            unit = i["unit"],
            is_mutli_type_unit = i["is_multi_type_unit"],
        )
        prodcut_list.append({"id":prod.id, "name":i["name"]})
    return prodcut_list

def fix_product():
    Products.objects.update(net_quantity = 0)  
    Stocks.objects.all().delete()
    Barcodes.objects.filter(is_product_type = True).delete()


#################### NEW SCRIPTS FOR STOCK IN & OUT


# def prod_stock_in(prod, quantity, create_date):
#     source_list = ["Local Markets", "Main Office", "Supplier Network", 
#         "Water Treatment Plant", "Power Plant", "Chemical Lab",
#         "Maintenance Shop", "Scrap Yard", "Storage Warehouse", "Finishing Area",
#         "Rolling Mill", "Steel Making Shop", "Raw Material Yard", "Blast Furnace"]
    
#     rack = random.choice(Racks.objects.all())
#     barcode= Barcodes.objects.create(is_product_type = True, status = "Used")
#     source = random.choice(source_list)
#     stock = Stocks.objects.create(product = prod, source = source, rack = rack, barcode = barcode, quantity = quantity, created_at = create_date, updated_at = create_date)
#     net_quantity = prod.net_quantity + quantity
#     prod.net_quantity = net_quantity
#     prod.save()
#     user = random.choice(Users.objects.all())
#     StocksHistory.objects.create(stock = stock, quantity = quantity, product_quantity = net_quantity, user = user, is_stock_out = False, created_at = create_date, updated_at = create_date)  
#     return stock


# def prod_stock_out(stock, quantity, create_date):
#     if stock.quantity >= quantity:
#         prod = stock.product
#         net_quantity = prod.net_quantity - quantity
#         prod.net_quantity = net_quantity
#         prod.save()
#         stock.quantity -= quantity
#         stock.save()
#         user = random.choice(Users.objects.all())
#         StocksHistory.objects.create(stock = stock, quantity = quantity, product_quantity = net_quantity, user = user, is_stock_out = True, created_at = create_date, updated_at = create_date)
#     else:
#         print(f'Stock Not Found or Huge Stock Quantity {stock.product.name}')


# def create_date_range(start_date, end_date):
#     date_list = []
#     current_date = start_date
#     while current_date <= end_date:
#         date_list.append(current_date)
#         current_date += timedelta(days=1)  # Increment by one day
#     return date_list

# def generate_stock_in_quantity():
#     # Generate a random quantity between 100 and 1000
#     return random.randint(50, 100)

# def generate_stock_out_quantity(quant):
#     return random.randint(int(quant*(9.5/10)), quant)


# def stock_in_out(start_date, end_date):
#     start_date = datetime.strptime(start_date, "%Y-%m-%d")    
#     end_date = datetime.strptime(end_date, "%Y-%m-%d")
#     date_list = create_date_range(start_date, end_date)
#     print("days length", len(date_list))
#     all_products = Products.objects.all()

#     for dt in date_list:
#         random_products = random.sample(list(all_products), k=10)
#         stock_in_list = []
#         range_length = random.randint(5, 10)
#         for _ in range(1, range_length):
#             quantity = generate_stock_in_quantity()
#             product = random.choice(random_products)
#             time_now = datetime.now().time()
#             create_at = dt + timedelta(hours = time_now.hour, minutes = time_now.minute, seconds = time_now.second, microseconds = time_now.microsecond) 
#             stock_in_list.append(prod_stock_in(product, quantity, create_at))

#         for s in stock_in_list:
#             s_quantity = generate_stock_out_quantity(s.quantity)
#             time_now = datetime.now().time()
#             create_at = dt + timedelta(hours = time_now.hour, minutes = time_now.minute, seconds = time_now.second, microseconds = time_now.microsecond) 
#             prod_stock_out(s, s_quantity, create_at)
#             stock_in_list.remove(s)

#         print(f'Date {dt} in-out {range_length}')





################# TEST  V2 ###################


def prod_stock_in(prod, quantity, create_date):
    if prod is None:
        print("Error: product should not be None")
        return None
    source_list = ["Local Markets", "Main Office", "Supplier Network",
                   "Water Treatment Plant", "Power Plant", "Chemical Lab",
                   "Maintenance Shop", "Scrap Yard", "Storage Warehouse", "Finishing Area",
                   "Rolling Mill", "Steel Making Shop", "Raw Material Yard", "Blast Furnace"]
    rack = random.choice(Racks.objects.all()) if Racks.objects.all() else None
    barcode = Barcodes.objects.create(is_product_type=True, status="Used")
    source = random.choice(source_list)
    stock = Stocks.objects.create(product=prod, source=source, rack=rack, barcode=barcode, quantity=quantity,
                                  created_at=create_date, updated_at=create_date)
    prod.net_quantity += quantity
    prod.save()
    user = random.choice(Users.objects.all()) if Users.objects.all() else None
    StocksHistory.objects.create(stock=stock, quantity=quantity, product_quantity=prod.net_quantity,
                                 user=user, is_stock_out=False, created_at=create_date, updated_at=create_date)
    return stock

def prod_stock_out(stock, quantity, create_date):
    if stock is None:
        print("Error: stock should not be None")
        return
    if stock.quantity >= quantity:
        prod = stock.product
        prod.net_quantity -= quantity
        prod.save()
        stock.quantity -= quantity
        stock.save()
        user = random.choice(Users.objects.all()) if Users.objects.all() else None
        purpose_list = ["Repair", "Replacement", "Maintenance", "New Installed", "Missing"]
        purpose = random.choice(purpose_list)
        employee = random.choice(Employees.objects.all()) if Employees.objects.all() else None
        StocksHistory.objects.create(stock=stock, quantity=quantity, product_quantity=prod.net_quantity,
                                     purpose = purpose, employee = employee,
                                     user=user, is_stock_out=True, created_at=create_date, updated_at=create_date)
    else:
        print(f'Insufficient stock for product {stock.product.name}')

def generate_stock_in_quantity(date_len):
    return random.randint(500, 1000) if date_len < 15 else random.randint(1, 100)

def generate_stock_out_quantity(stock_quantity):
    return random.randint(int((stock_quantity) * (90/100)), stock_quantity)

def is_new_month(current_date, last_date):
    return current_date.month != last_date.month or current_date.year != last_date.year

def generate_dates(start_date, end_date):
    current_date = start_date
    dates = []
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)
    return dates



def stock_in_out(start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    all_dates = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
    total_days = len(all_dates)
    # Initialize only once, to carry over for subsequent months
    total_stock_left = 0#random.randint(1000, 5000)
    monthly_stock_in = 0
    monthly_stock_out = 0
    monthly_stock_in_count = 0
    monthly_stock_out_count = 0
    last_date = start_date - timedelta(days=1)
    stock_in_list = []
    # Holds all the stock-in records for random stock-out selection
    all_products = Products.objects.all()
    for dt in all_dates:
        random_products = random.sample(list(all_products), k=10)
        if dt.month != last_date.month or dt.year != last_date.year:
            print(f"For month {last_date.strftime('%Y-%m')}: Total Stock Left: {total_stock_left}, Stock In: {monthly_stock_in}, Stock Out: {monthly_stock_out}, Count IN-{monthly_stock_in_count}|| OUT-{monthly_stock_out_count}")            
            # Reset monthly counters, but carry over total_stock_left
            monthly_stock_in = 0
            monthly_stock_out = 0
            monthly_stock_in_count = 0
            monthly_stock_out_count = 0
        # Decide the number of stock-in/out operations for the day
        range_length = random.randint(5, 10)
        for _ in range(range_length):
            #action_prob = random.random()
            action_amount = 2000 if dt.month % 2 == 0 else 2500
            if total_stock_left < action_amount:
                prod = random.choice(random_products)  # Replace with actual logic
                stock_in_today = generate_stock_in_quantity(total_days)

                if stock_in := prod_stock_in(prod, stock_in_today, datetime.combine(dt, datetime.now().time())):
                    stock_in_list.append(stock_in)

                total_stock_left += stock_in_today
                monthly_stock_in += stock_in_today
                monthly_stock_in_count += 1

            elif total_stock_left > 0:
                s = random.choice(stock_in_list) if stock_in_list else None
                if s:
                    s_quantity = generate_stock_out_quantity(s.quantity)
                    prod_stock_out(s, s_quantity, datetime.combine(dt, datetime.now().time()))
                    total_stock_left -= s_quantity
                    monthly_stock_out += s_quantity
                    monthly_stock_out_count += 1
                    stock_in_list.remove(s)
                else:
                    prod = random.choice(random_products)  # Replace with actual logic
                    stock_in_today = generate_stock_in_quantity(total_days)

                    if stock_in := prod_stock_in(prod, stock_in_today, datetime.combine(dt, datetime.now().time())):
                        stock_in_list.append(stock_in)

                    total_stock_left += stock_in_today
                    monthly_stock_in += stock_in_today
                    monthly_stock_in_count += 1
                    
        last_date = dt


def fix_user_secret_token():
    for i in Users.objects.all():
        i.secret_token = encrypt_user_secret_token(i.email)
        i.save()
    print("All user secret token stored properly")