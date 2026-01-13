from AdminApp.models import *
from AuthApp.models import *
from django.db import transaction
from django.db.models import Q
from AdminApp.utils import Syserror
import random
from datetime import datetime, timedelta
import math



def prod_stock_in(create_date=None):
    stock_in_type_list = ["NEW MATERIAL", "RETURN MATERIAL", "BORROWING MATERIAL", "RECEIVE LENT MATERIAL"]
    stock_in_type = random.choices(stock_in_type_list, weights=[75, 5, 10, 10], k=1)[0]
    try:
        if create_date is None:
            create_date=datetime.now()
        
        barcode = None
        expired_date = None
        lent_material_stock = None

        if stock_in_type == "RETURN MATERIAL":
            stock_histories = StocksHistory.objects.filter(history_type="MATERIAL CONSUMPTION", is_stock_out=True, created_at__lte = create_date)

            if not stock_histories.exists():
                raise ValueError(f"Stock history not found for MATERIAL CONSUMPTION")
            
            stock_history = stock_histories.first()
            stock = stock_history.stock
            barcode = stock.barcode
            prod = stock.product
            quantity = random.randint(math.ceil(stock_history.quantity*0.8) , stock_history.quantity) if prod.is_mutli_type_unit else 1
            source = stock.source
            rack = stock.rack

        else:
            rack = random.choice(Racks.objects.all())
            is_perishable_stockin = random.choices([False, True], weights=[80, 20], k=1)[0] # False means select none Perishable product
            if is_perishable_stockin:
                expired_date = create_date + timedelta(days=random.randint(10, 30))

            if stock_in_type == "RECEIVE LENT MATERIAL":
                old_lent_stock = BorrowedStock.objects.filter(lent_quantity__gt=0)
                if old_lent_stock:
                    lent_stock = random.choice(old_lent_stock)
                    source = lent_stock.source
                    prod = lent_stock.product
                    quantity  =  random.randint(math.ceil(lent_stock.lent_quantity*0.8) , lent_stock.lent_quantity) if prod.is_mutli_type_unit else 1
                    lent_material_stock = lent_stock
                else:
                    stock_in_type = "NEW MATERIAL"
                    prod = random.choice(Products.objects.filter(perishable_product=is_perishable_stockin))
                    source = random.choice(Source.objects.filter(is_central_store=stock_in_type == "NEW MATERIAL"))
                    quantity  =  random.randint(math.ceil(prod.min_threshold*0.2) , prod.min_threshold) if prod.is_mutli_type_unit else 1

            else:
                prod = random.choice(Products.objects.filter(perishable_product=is_perishable_stockin))
                source = random.choice(Source.objects.filter(is_central_store=stock_in_type == "NEW MATERIAL"))
                quantity  =  random.randint(math.ceil(prod.min_threshold*0.2) , prod.min_threshold) if prod.is_mutli_type_unit else 1

        with transaction.atomic():
            # handle return Material Case
            if barcode  is None:
                barcode = Barcodes.objects.create(is_product_type=True, status="Used")
                stock = Stocks.objects.create(
                    product=prod,
                    source=source,
                    rack=rack,
                    barcode=barcode,
                    quantity=quantity,
                    created_at=create_date,
                    updated_at=create_date,
                    expired_date=expired_date,
                )
            else:
                stock.quantity += quantity
                stock.save()
                
            prod.net_quantity += quantity
            prod.save()

            user = random.choice(Users.objects.all()) if Users.objects.all() else None
            StocksHistory.objects.create(
                stock=stock,
                quantity=quantity,
                product_quantity=prod.net_quantity,
                user=user,
                is_stock_out=False,
                history_type=stock_in_type,
                created_at=create_date,
                updated_at=create_date
            )

            if stock_in_type == "BORROWING MATERIAL":
                borrowed, _ = BorrowedStock.objects.get_or_create(product=prod, source=source)
                borrowed.borrowed_quantity += quantity
                borrowed.save()

            if stock_in_type == "RECEIVE LENT MATERIAL" and lent_material_stock:
                lent_material_stock.lent_quantity -= quantity
                lent_material_stock.save()

            return stock
        
    except Exception as e:
        Syserror(e)
        print(f"EXECUTION FAILED STOCK IN {stock_in_type}")
        return None



def prod_stock_out(create_date=None):
    stock_out_type_list = ["MATERIAL CONSUMPTION", "RETURN BORROWED MATERIAL", "LENDING MATERIAL"]
    stock_out_type = random.choices(stock_out_type_list, weights=[80, 10, 10], k=1)[0]
    try:
        if create_date is None:
            create_date = datetime.now()

        user = random.choice(Users.objects.all()) if Users.objects.all() else None
        purpose_list = [
            "Repair",
            "Replacement",
            "Maintenance",
            "New Installed",
            "Missing",
        ]

        purpose = random.choice(purpose_list)
        employee = random.choice(Employees.objects.all()) if Employees.objects.all() else None
        stock_filter = Q(quantity__gte=1)
        if stock_out_type == "RETURN BORROWED MATERIAL":
            try:
                old_borrowed_stock = random.choice(BorrowedStock.objects.filter(lent_quantity__gt=0))
                stock_filter &= Q(product=old_borrowed_stock.product, source=old_borrowed_stock.source)
            except:
                stock_out_type = "MATERIAL CONSUMPTION"

        stock_in_list = Stocks.objects.filter(stock_filter)
        obsolete_inventory_stock = None
        stock = random.choice(stock_in_list)
        product = stock.product
        quantity = random.randint(1, stock.quantity) if product.is_mutli_type_unit else 1

        with transaction.atomic():
            source = None
            if stock_out_type == "MATERIAL CONSUMPTION":
                purpose = purpose = random.choice(purpose_list)
            else:
                source = random.choice(Source.objects.filter(is_central_store=False))
                if stock_out_type == "LENDING MATERIAL":
                    lent_stock, created = BorrowedStock.objects.get_or_create(product=product, source=source)
                    lent_stock.lent_quantity += quantity
                    lent_stock.save()
                    purpose = f"Lent to {source.name}"

                else:  # Returning borrowed material
                    purpose = f"Returned to {source.name}"
                    borrowed_stock = BorrowedStock.objects.filter(product=product, source=source).first()
                    if quantity > borrowed_stock.borrowed_quantity:
                        quantity = random.randint(math.ceil(borrowed_stock.borrowed_quantity*0.5), borrowed_stock.borrowed_quantity) if product.is_mutli_type_unit else 1
                    borrowed_stock.borrowed_quantity -= quantity
                    borrowed_stock.save()

            stock.quantity -= quantity
            stock.save()
            product.net_quantity -= quantity
            product.save()

            obsolete_inventory_barcode = None
            if product.perishable_product:
                if (
                    lastStock := Stocks.objects.filter(
                        product=product,
                        quantity__gt=0,
                        expired_date__isnull=False,
                    )
                    .exclude(id=obsolete_inventory_stock)
                    .order_by("expired_date")
                    .first()
                ):
                    if lastStock != stock:
                        obsolete_inventory_barcode = lastStock.barcode.barcode_no
                obsolete_inventory_stock = stock.id

            StocksHistory.objects.create(
                stock=stock,
                quantity=quantity,
                history_type=stock_out_type,
                product_quantity=product.net_quantity,
                user=user,
                is_stock_out=True,
                employee=employee,
                purpose=purpose,
                created_at=create_date,
                updated_at=create_date,
                obsolete_inventory_barcode=obsolete_inventory_barcode,
            )
            return stock
    except Exception as e:
        Syserror(e)
        print(f"EXECUTION FAILED STOCK OUT {stock_out_type}")
        return None


def generate_stock_datetime(start_date_str, end_date_str):
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        current_date = start_date
        datetimes = []

        while current_date <= end_date:
            for _ in range(random.randint(5, 10)):  # Generate multiple times per day
                if random.random() < 0.8:  # 80% chance to fall in rush hours
                    hour = random.randint(9, 18)  # 9 AM to 6 PM
                else:
                    hour = random.choice([random.randint(0, 8), random.randint(19, 23)])  # Non-rush hours
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                new_datetime = current_date.replace(hour=hour, minute=minute, second=second)
                datetimes.append(new_datetime)
            current_date += timedelta(days=1)
        
        return datetimes
    except Exception as e:
        print("EXECUTAION FAILED")
        Syserror(e)
        return []
    
def start_auto_stockinout():
    start_date = input("Enter start date fromat like YYYY-MM-DD : ")
    end_date = input("Enter end date fromat like YYYY-MM-DD : ")
    datetime_list = generate_stock_datetime(start_date, end_date)
    success = {"IN":0, "OUT":0}
    failed = {"IN":0, "OUT":0}
    for create_date  in datetime_list:
        is_stockin = random.choices([True, False], weights=[70, 30], k=1)[0]
        create_date_repeat_count = random.choices([1, 2, 3, 4], weights=[60, 25, 10, 5], k=1)[0]
        for _ in range(create_date_repeat_count):
            result = prod_stock_in(create_date) if is_stockin else prod_stock_out(create_date)
            if result is None:
                failed["IN" if is_stockin else "OUT"] += 1
            else:
                success["IN" if is_stockin else "OUT"] += 1
    print(f"SUCCESS: {success} / FAILED: {failed}")


    
    




