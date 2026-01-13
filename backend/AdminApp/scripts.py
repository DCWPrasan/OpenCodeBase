from AdminApp.models import ProductCategory, Unit, Products, Racks, Barcodes, Employees, Source, Stocks, StocksHistory
from AuthApp.models import Designation, Users
import json
from django.utils.dateparse import parse_datetime

def parse_datetime_tznone(value):
    if value:
        dtime = parse_datetime(value)
        if dtime:
            return dtime.replace(tzinfo=None)
        if value.endswith('Z'):
            value = value[:-1] + '+00:00'
        return parse_datetime(value).replace(tzinfo=None)
    return None

def populate_product_categories(data):
    for item in data.get('productcategory', []):
        ProductCategory.objects.update_or_create(
            id=item['id'],
            defaults={
                'name': item['name'],
                'created_at': parse_datetime_tznone(item['created_at']),
                'updated_at': parse_datetime_tznone(item['updated_at'])
            }
        )

def populate_units(data):
    for item in data.get('unit', []):
        Unit.objects.update_or_create(
            id=item['id'],
            defaults={'name': item['name']}
        )

def populate_designations(data):
    for item in data.get('designations', []):
        Designation.objects.update_or_create(
            id=item['id'],
            defaults={
                'name': item['name'],
                'created_at': parse_datetime_tznone(item['created_at']),
                'updated_at': parse_datetime_tznone(item['updated_at'])
            }
        )

def populate_users(data):
    for item in data.get('users', []):
        designation = None
        if item['designation_id'] is not None:
            try:
                designation = Designation.objects.get(id=item['designation_id'])
            except Designation.DoesNotExist:
                print(f"Designation with id {item['designation_id']} does not exist. Skipping user creation.")
                
        password=f"{item['personnel_number']}@123"
        user, created  = Users.objects.update_or_create(
            id=item['id'],
            defaults={
                'role': item['role'],
                'personnel_number': item['personnel_number'],
                'email': item['email'],
                'name': item['name'],
                'is_superuser': item['is_superuser'],
                'is_staff': item['is_staff'],
                'is_active': item['is_active'],
                'mobile_number': item['mobile_number'],
                'date_joined': parse_datetime_tznone(item['date_joined']),
                'last_login': parse_datetime_tznone(item['last_login']),
                'created_at': parse_datetime_tznone(item['created_at']),
                'updated_at': parse_datetime_tznone(item['updated_at']),
                'designation': designation
            }
        )
        user.set_password(password)
        user.save()

def populate_employees(data):
    for item in data.get('employees', []):
        Employees.objects.update_or_create(
            id=item['id'],
            defaults={
                'name': item['name'],
                'phone': item['phone'],
                'personnel_number': item['personnel_number'],
                'created_at': parse_datetime_tznone(item['created_at']),
                'updated_at': parse_datetime_tznone(item['updated_at']),
            }
        )

def populate_products(data):
    for item in data.get('products', []):
        category = None
        if item['category_id'] is not None:
            try:
                category = ProductCategory.objects.get(id=item['category_id'])
            except ProductCategory.DoesNotExist:
                print(f"ProductCategory with id {item['category_id']} does not exist. Skipping product creation.")

        Products.objects.update_or_create(
            id=item['id'],
            defaults={
                'name': item['name'],
                'ucs_code': item['ucs_code'],
                'description': item['description'],
                'description_sap': item.get('description_sap') or None,
                'min_threshold': item['min_threshold'],
                'max_threshold': item['max_threshold'],
                'net_quantity': item['net_quantity'],
                'price': item['price'],
                'is_mutli_type_unit': True,
                'perishable_product': False,
                'lead_time': item['lead_time'],
                'created_at': parse_datetime_tznone(item['created_at']),
                'updated_at': parse_datetime_tznone(item['updated_at']),
                'category': category,
                'unit_id': item['unit_id']
            }
        )

def populate_racks(data):
    for item in data.get('racks', []):
        try:
            barcode = Barcodes.objects.get(id=item['barcode_id'])
        except Barcodes.DoesNotExist:
            print(f"Barcode with id {item['barcode_id']} does not exist. Skipping user creation.")
            continue
        Racks.objects.update_or_create(
            id=item['id'],
            defaults={
                'rack_no': item['rack_no'],
                'barcode': barcode,
                'created_at': parse_datetime_tznone(item['created_at']),
                'updated_at': parse_datetime_tznone(item['updated_at'])
            }
        )

def populate_barcodes(data):
    for item in data.get('barcodes', []):
        Barcodes.objects.update_or_create(
            id=item['id'],
            defaults={
                'barcode_no': item['barcode_no'],
                'is_product_type': item['is_product_type'],
                'status': item['status'],
                'created_at': parse_datetime_tznone(item['created_at']),
                'updated_at': parse_datetime_tznone(item['updated_at'])
            }
        )

def populate_stocks(data):
    for item in data.get("stocks", []):
        try:
            product = Products.objects.get(id=item["product_id"])
            barcode = Barcodes.objects.get(id=item["barcode_id"])
            rack = Racks.objects.get(id=item["rack_id"])
            source_name = item["source"].strip()
            source, _ = Source.objects.get_or_create(name=source_name)

            # Ensure datetime is timezone-aware
            created_at = parse_datetime_tznone(item["created_at"])
            updated_at = parse_datetime_tznone(item["updated_at"])

            Stocks.objects.update_or_create(
                id=item["id"],
                defaults={
                    "product": product,
                    "barcode": barcode,
                    "rack": rack,
                    "source": source,
                    "quantity": float(item["quantity"]),
                    "expired_date": None,  # Assuming no expiry in input
                    "created_at": created_at,
                    "updated_at": updated_at,
                },
            )
            print(f"✅ Stock {item['id']} saved or updated.")
        except Products.DoesNotExist:
            print(f"❌ Product not found: {item['product_id']}")
        except Barcodes.DoesNotExist:
            print(f"❌ Barcode not found: {item['barcode_id']}")
        except Racks.DoesNotExist:
            print(f"❌ Rack not found: {item['rack_id']}")
        except Exception as e:
            print(f"⚠️ Error saving stock {item['id']}: {e}")

def populate_stocks_history(data):
    for item in data.get("stocks_history", []):
        try:
            stock = Stocks.objects.get(id=item["stock_id"])
            user = Users.objects.get(id=item["user_id"]) if item["user_id"] else None
            employee = Employees.objects.get(id=item["employee_id"]) if item["employee_id"] else None

            created_at = parse_datetime_tznone(item["created_at"])
            updated_at = parse_datetime_tznone(item["updated_at"])
            if item["is_stock_out"]:
                history_type="MATERIAL CONSUMPTION"
            else:
                history_type="NEW MATERIAL"
            StocksHistory.objects.update_or_create(
                id=item["id"],
                defaults={
                    "stock": stock,
                    "history_type": "ADDED",  # Adjust if you use other types like 'REMOVED'
                    "purpose": item.get("purpose"),
                    "employee": employee,
                    "history_type":history_type,
                    "quantity": float(item["quantity"]),
                    "product_quantity": float(item["product_quantity"]),
                    "is_stock_out": item["is_stock_out"],
                    "user": user,
                    "obsolete_inventory_barcode": None,
                    "created_at": created_at,
                    "updated_at": updated_at,
                }
            )
            print(f"✅ Saved history: {item['id']}")
        except Stocks.DoesNotExist:
            print(f"❌ Stock not found: {item['stock_id']}")
        except Users.DoesNotExist:
            print(f"❌ User not found: {item['user_id']}")
        except Employees.DoesNotExist:
            print(f"❌ Employee not found: {item['employee_id']}")
        except Exception as e:
            print(f"⚠️ Error saving history {item['id']}: {e}")

def import_data():
    file_path = 'data.json'
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print("🚀 Starting data import...")
    populate_product_categories(data)
    populate_units(data)
    populate_barcodes(data)
    populate_designations(data)
    populate_users(data)
    populate_employees(data)
    populate_products(data)
    populate_racks(data)
    populate_stocks(data)
    populate_stocks_history(data)
    print("✅ Data import completed.")