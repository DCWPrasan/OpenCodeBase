from django.db import models
from AdminApp.utils import getId, generate_barcode
from AuthApp.models import Users
from django.utils import timezone

VED_CATEGORY_CHOICE = [
    ("Vital", "VITAL"),
    ("Essential", "ESSENTIAL"),
    ("Desirable","DESIRABLE")
]

class Barcodes(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    barcode_no = models.CharField(max_length=250, null=True)
    is_product_type = models.BooleanField(default=True)
    status = models.CharField(max_length=6, default="Used")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('bcd_')
            while Barcodes.objects.filter(id=self.id).exists():
                self.id = getId('bcd_')
        if not self.barcode_no:
            prefix = 'P' if self.is_product_type else 'R'
            self.barcode_no = generate_barcode(prefix)
            while Barcodes.objects.filter(barcode_no=self.barcode_no).exists():
                self.barcode_no = generate_barcode(prefix)
        super(Barcodes, self).save()

class Racks(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    rack_no = models.CharField(max_length=120)
    barcode = models.OneToOneField(Barcodes, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('rck_')
            while Racks.objects.filter(id=self.id).exists():
                self.id = getId('rck_')
        super(Racks, self).save()

class Employees(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    email = models.EmailField(('email address'), unique=True)
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=10,null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('emp_')
            while Employees.objects.filter(id=self.id).exists():
                self.id = getId('emp_')
        super(Employees, self).save()

class ProductCategory(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    name = models.CharField(max_length=235)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId("pct_")
            while ProductCategory.objects.filter(id=self.id).exists():
                self.id = getId("pct_")
        super(ProductCategory, self).save()

class Unit(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    name = models.CharField(max_length=235)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId("unt_")
            while Unit.objects.filter(id=self.id).exists():
                self.id = getId("unt_")
        super(Unit, self).save()

class Products(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    name = models.CharField(max_length=250, db_index=True)
    ucs_code = models.CharField(max_length=250, unique=True, db_index=True)
    description = models.TextField(null=True)
    description_sap = models.TextField(null=True)
    min_threshold = models.IntegerField()
    max_threshold = models.IntegerField(null=True)
    net_quantity = models.IntegerField(default=0)
    price = models.FloatField(default=0)
    is_mutli_type_unit = models.BooleanField(default=False)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True)
    ved_category = models.CharField(max_length=20, choices=VED_CATEGORY_CHOICE, default=VED_CATEGORY_CHOICE[0][0])
    lead_time = models.IntegerField(default=1, help_text="Lead time in days")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('prod_')
            while Products.objects.filter(id=self.id).exists():
                self.id = getId('prod_')
        super(Products, self).save()

class Stocks(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    source = models.TextField(db_index=True)
    rack = models.ForeignKey(Racks, on_delete=models.SET_NULL, null=True, db_index=True)
    barcode = models.OneToOneField(Barcodes, on_delete=models.CASCADE, db_index=True)
    quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('stk_')
            while Stocks.objects.filter(id=self.id).exists():
                self.id = getId('stk_')
        super(Stocks, self).save()
    

class StocksHistory(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    stock = models.ForeignKey(Stocks, on_delete=models.CASCADE)
    purpose = models.TextField(null=True)
    employee = models.ForeignKey(Employees, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0)
    product_quantity = models.IntegerField(default=0)
    is_stock_out = models.BooleanField(default=True)
    user = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('sth_')
            while StocksHistory.objects.filter(id=self.id).exists():
                self.id = getId('sth_')
        super(StocksHistory, self).save()
