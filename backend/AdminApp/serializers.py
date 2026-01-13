from rest_framework import serializers
from .models import (
    Products,
    Racks,
    Stocks,
    StocksHistory,
    Barcodes,
    ProductCategory,
    Employees,
    Unit,
    Source,
    Requisition, 
    RequisitionItem,
    Reservation,
    ReservationItem
)
from AuthApp.models import Users, Designation
from django.db.models import Sum

class RacksSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(RacksSerializer, self).to_representation(obj)
        ret["product"] = obj.product if hasattr(obj, "product") else 0
        ret["barcode_no"] = obj.barcode.barcode_no
        return ret

    class Meta:
        model = Racks
        fields = ["id", "rack_no"]
        read_only_fields = fields

class RackStocksSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(RackStocksSerializer, self).to_representation(obj)
        ret["barcode"] = obj.barcode.barcode_no
        ret["created_at"] = obj.created_at.strftime("%d %b %Y %I:%M %p")
        ret["expired_date"] = obj.expired_date.strftime("%d %b %Y") if obj.expired_date else None
        return ret

    class Meta:
        model = Stocks
        fields = ["id", "quantity"]
        read_only_fields = fields


class RacksProductDetailsSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(RacksProductDetailsSerializer, self).to_representation(obj)
        rack_id = self.context.get("rack_id")
        rack_stock = Stocks.objects.select_related("product", "rack").filter(product=obj, rack__id=rack_id, quantity__gt=0)
        ret["stocks"] = RackStocksSerializer(rack_stock, many=True).data
        ret['net_quantity']= rack_stock.aggregate(net=Sum("quantity"))["net"]
        return ret

    class Meta:
        model = Products
        fields = ["id", "name", "ucs_code"]
        read_only_fields = fields


class SearchRequisitionsSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(SearchRequisitionsSerializer, self).to_representation(obj)
        ret["label"] = obj.reference_no
        ret["value"] = obj.id
        return ret

    class Meta:
        model = Requisition
        fields = []

class SearchReservationtionsSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(SearchReservationtionsSerializer, self).to_representation(obj)
        ret["label"] = obj.reference_no
        ret["value"] = obj.id
        return ret

    class Meta:
        model = Reservation
        fields = []
        
class SearchRacksSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(SearchRacksSerializer, self).to_representation(obj)
        ret["label"] = obj.rack_no
        ret["value"] = obj.id
        return ret

    class Meta:
        model = Racks
        fields = []


class SearchEmployeeSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(SearchEmployeeSerializer, self).to_representation(obj)
        ret["label"] = f"{obj.name} ({obj.personnel_number})" if obj.personnel_number else obj.name
        ret["value"] = obj.id
        return ret

    class Meta:
        model = Employees
        fields = []


class ProductsSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(ProductsSerializer, self).to_representation(obj)
        ret["unit"] = {"id": obj.unit.id, "name": obj.unit.name}
        return ret
    class Meta:
        model = Products
        fields = [
            "id",
            "name",
            "ucs_code",
            "net_quantity",
            "price",
            "unit",
            "min_threshold",
            "max_threshold",
        ]
        read_only_fields = fields


class StocksSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(StocksSerializer, self).to_representation(obj)
        ret["product"] = obj.product.name
        ret["rack"] = obj.rack.rack_no
        return ret

    class Meta:
        model = Stocks
        fields = ["id", "quantity"]
        read_only_fields = fields

class StocksRecommendedSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(StocksRecommendedSerializer, self).to_representation(obj)
        ret["rack"] = obj.rack.rack_no
        ret["barcode"] = obj.barcode.barcode_no
        ret["created_at"] = obj.created_at.strftime("%d %b %Y")
        ret["expired_date"] = obj.expired_date.strftime("%d %b %Y") if obj.expired_date else None
        return ret

    class Meta:
        model = Stocks
        fields = ["id", "quantity"]
        read_only_fields = fields


class ProductStocksSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(ProductStocksSerializer, self).to_representation(obj)
        ret["rack"] = {
            "rack_no":obj.rack.rack_no,
            "id":obj.rack.id
        }
        ret["barcode"] = obj.barcode.barcode_no
        ret["created_at"] = obj.created_at.strftime("%d %b %Y")
        ret["expired_date"] = obj.expired_date.strftime("%d %b %Y") if obj.expired_date else None
        return ret

    class Meta:
        model = Stocks
        fields = ["id", "quantity"]
        read_only_fields = fields


class PerishableStocksSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(PerishableStocksSerializer, self).to_representation(obj)
        ret["product"] = {
            "name":obj.product.name,
            "id": obj.product.id,
        }
        ret["rack"] = obj.rack.rack_no
        ret["barcode"] = obj.barcode.barcode_no
        ret["expired_date"] = obj.expired_date.strftime("%d %b %Y") if obj.expired_date else None
        return ret

    class Meta:
        model = Stocks
        fields = ["id", "quantity"]
        read_only_fields = fields

class StocksHistorySerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(StocksHistorySerializer, self).to_representation(obj)
        ret["user"] = {"name": obj.user.name, "email": obj.user.email} if obj.user else None
        ret["employee"] = (
            {"name": obj.employee.name, "personnel_number": obj.employee.personnel_number}
            if obj.employee
            else None
        )
        ret["stock"] = {
            "product": {
                "name": obj.stock.product.name,
                "id": obj.stock.product.id,
                "ucs_code": obj.stock.product.ucs_code,
                "price": obj.stock.product.price,
            },
            "rack": {"id": obj.stock.rack.id, "rack_no": obj.stock.rack.rack_no}
            if obj.stock.rack
            else None,
            "barcode_no": obj.stock.barcode.barcode_no,
        }
        ret["source"]= obj.source.name if obj.source else None
        ret["created_at"] = obj.created_at.strftime("%d %b %Y, %I:%M %p")
        return ret

    class Meta:
        model = StocksHistory
        fields = ["id", "quantity", "is_stock_out", "product_quantity", "purpose", "history_type", "reference_no"]
        read_only_fields = fields


class BarcodeSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(BarcodeSerializer, self).to_representation(obj)
        product = None
        if hasattr(obj, "stocks"):
            if stock:=obj.stocks.first():
                product = stock.product
        ret["product"] = (
            {"id": product.id, "name": product.name}
            if product
            else None
        )
        ret["rack"] = (
            {"id": obj.racks.id, "rack_no": obj.racks.rack_no}
            if hasattr(obj, "racks")
            else None
        )
        ret["created_at"] = obj.created_at.strftime("%Y-%m-%d %I:%M: %p")
        return ret

    class Meta:
        model = Barcodes
        fields = ["id", "barcode_no", "status"]
        read_only_fields = fields


class ProductsDetailsSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(ProductsDetailsSerializer, self).to_representation(obj)
        ret["category"] = (
            {"id": obj.category.id, "name": obj.category.name} if obj.category else None
        )
        ret["unit"] = {"id": obj.unit.id, "name": obj.unit.name}
        return ret

    class Meta:
        model = Products
        fields = [
            "id",
            "name",
            "net_quantity",
            "price",
            "unit",
            "min_threshold",
            "max_threshold",
            "is_mutli_type_unit",
            "description",
            "description_sap",
            "ucs_code",
            "lead_time",
            "ved_category",
            "perishable_product",
            "is_active"
        ]
        read_only_fields = fields


class UserSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(UserSerializer, self).to_representation(obj)
        ret["designation"] = (
            {"id": obj.designation.id, "name": obj.designation.name}
            if obj.designation
            else None
        )
        ret["status"] = "Active" if obj.is_active else "Inactive"
        return ret

    class Meta:
        model = Users
        fields = ["id", "name", "email", "mobile_number", "personnel_number", "is_allow_email_daily_report", "is_allow_email_low_stock_alert", "user_permission"]
        read_only_fields = fields



class RequisitionItemStockoutSerializer(serializers.ModelSerializer):

    def to_representation(self, obj):
        ret = super(RequisitionItemStockoutSerializer, self).to_representation(obj)
        ret["product"] = {
            "id": obj.product.id,
            "name": obj.product.name,
            "is_multi_unit":obj.product.is_mutli_type_unit,
            "perishable_product": obj.product.perishable_product
        }
        return ret

    class Meta:
        model = RequisitionItem
        fields = ["id", "requested_quantity", "fulfilled_quantity", "purpose",]
        

class ReservationItemStockinSerializer(serializers.ModelSerializer):

    def to_representation(self, obj):
        ret = super(ReservationItemStockinSerializer, self).to_representation(obj)
        ret["product"] = {
            "id": obj.product.id,
            "name": obj.product.name,
            "is_multi_unit":obj.product.is_mutli_type_unit,
            "perishable_product": obj.product.perishable_product
        }
        ret["source"] = {
            "id": obj.source.id,
            "name": obj.source.name
        } if obj.source else None
        return ret

    class Meta:
        model = ReservationItem
        fields = ["id", "quantity", "source",]


class RequisitionItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = RequisitionItem
        fields = ["id", "product", "product_name", "requested_quantity", "fulfilled_quantity", "purpose"]


class RequisitionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Requisition
        fields = [
            "id",
            "reference_no",
            "status",
            "fulfillment_date",
            "total_material",
            "total_quantity",
            "created_at",
            "updated_at",
        ]

        extra_kwargs = {
            "created_at": {"format": "%d %b %Y %I:%M %p"},
            "updated_at": {"format": "%d %b %Y %I:%M %p"},
            "fulfillment_date": {"format": "%d %b %Y"},
        }
    
    def to_representation(self, instance):
        ret = super(RequisitionSerializer, self).to_representation(instance)
        ret["requested_by"] = {
            "id": instance.requested_by.id,
            "name": instance.requested_by.name,
            "personnel_number": instance.requested_by.personnel_number,
        } if instance.requested_by else None
        if self.context.get("include_items", False):
            ret["items"] = RequisitionItemSerializer(instance.items.all(), many=True).data
        return ret
    

class ReservationItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    source_name = serializers.CharField(source="source.name", read_only=True)

    class Meta:
        model = ReservationItem
        fields = ["id", "product", "product_name", "quantity", "source", "source_name"]


class ReservationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reservation
        fields = [
            "id",
            "reservation_type",
            "reference_no",
            "status",
            "reason",
            "total_material",
            "total_quantity",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "created_at": {"format": "%d %b %Y %I:%M %p"},
            "updated_at": {"format": "%d %b %Y %I:%M %p"},
        }
    
    def to_representation(self, instance):
        ret = super(ReservationSerializer, self).to_representation(instance)
        ret["reserved_by"] = {
            "id": instance.reserved_by.id,
            "name": instance.reserved_by.name,
            "personnel_number": instance.reserved_by.personnel_number,
        } if instance.reserved_by else None
        if self.context.get("include_items", False):
            ret["items"] = ReservationItemSerializer(instance.items.all(), many=True).data
        return ret

class DesignationSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(DesignationSerializer, self).to_representation(obj)
        ret["label"] = obj.name
        ret["value"] = obj.id
        return ret

    class Meta:
        model = Designation
        fields = []
        
class UnitSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(UnitSerializer, self).to_representation(obj)
        ret["label"] = obj.name
        ret["value"] = obj.id
        return ret

    class Meta:
        model = Unit
        fields = []

class SourceSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(SourceSerializer, self).to_representation(obj)
        ret["label"] = obj.name
        ret["value"] = obj.id
        return ret

    class Meta:
        model = Source
        fields = ["is_central_store"]


class SearchMaterialSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(SearchMaterialSerializer, self).to_representation(obj)
        if self.context.get("include_net_quantity", False):
            ret["label"] = f"{obj.name} (NQ: {int(obj.net_quantity)})\nUCS-{obj.ucs_code}"
        else:
            ret["label"] = obj.name
        ret["value"] = obj.id
        ret["is_multi_unit"] = obj.is_mutli_type_unit
        ret["perishable_product"] = obj.perishable_product 
        return ret

    class Meta:
        model = Products
        fields = []


class EmployeeSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(EmployeeSerializer, self).to_representation(obj)
        ret["material"] = obj.product if hasattr(obj, "product") else 0
        return ret

    class Meta:
        model = Employees
        fields = ["id", "name", "personnel_number", "phone"]


class ProductCategorySerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(ProductCategorySerializer, self).to_representation(obj)
        ret["label"] = obj.name
        ret["value"] = obj.id
        return ret

    class Meta:
        model = ProductCategory
        fields = []


# report


class ReportMaterialSerializer(serializers.Serializer):
    material_name = serializers.CharField(source="stock__product__name")
    ucs_code = serializers.CharField(source="stock__product__ucs_code")
    total_stock_in = serializers.IntegerField()
    total_stock_in_price = serializers.IntegerField()
    total_stock_out = serializers.IntegerField()
    total_stock_out_price = serializers.IntegerField()

    class Meta:
        fields = (
            "material_name",
            "ucs_code",
            "total_stock_in",
            "total_stock_in_price",
            "total_stock_out",
            "total_stock_out_price",
        )


class ReportMaterialTransacrionSerializer(serializers.Serializer):
    material_name = serializers.CharField(source="stock__product__name")
    ucs_code = serializers.CharField(source="stock__product__ucs_code")
    total_stock_in = serializers.IntegerField()
    total_stock_out = serializers.IntegerField()
    date = serializers.DateField(source="created_at__date", format="%d %b %Y")

    class Meta:
        fields = (
            "material_name",
            "ucs_code",
            "total_stock_in",
            "total_stock_out",
            "date",
        )


class ReportFastReceiveMovingItemSerializer(serializers.Serializer):
    material_name = serializers.CharField(source="name")
    ucs_code = serializers.CharField()
    quantity = serializers.IntegerField()

    class Meta:
        fields = ("material_name", "ucs_code", "quantity")


class CrirticalReorderItemSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source="name")

    class Meta:
        model = Products
        fields = ("material_name", "ucs_code", "net_quantity", "min_threshold")
        read_only_fields = fields


class ReportEmployeeSerializer(serializers.Serializer):
    employee_name = serializers.CharField(source="employee__name")
    employee_personnel_number = serializers.CharField(source="employee__personnel_number")
    material_name = serializers.CharField(source="stock__product__name")
    ucs_code = serializers.CharField(source="stock__product__ucs_code")
    total_stock_out = serializers.IntegerField()
    total_stock_out_price = serializers.IntegerField()

    class Meta:
        fields = (
            "employee_name",
            "employee_personnel_number",
            "material_name",
            "ucs_code",
            "total_stock_out",
            "total_stock_out_price",
        )


class ReportMaterialUsageSerializer(serializers.Serializer):
    purpose = serializers.CharField()
    material_name = serializers.CharField(source="stock__product__name")
    ucs_code = serializers.CharField(source="stock__product__ucs_code")
    total_stock_out = serializers.IntegerField()

    class Meta:
        fields = ("purpose", "material_name", "ucs_code", "total_stock_out")


class ReportInventoryExceptionSerializer(serializers.Serializer):
    actual_barcode = serializers.CharField(source="obsolete_inventory_barcode")
    barcode = serializers.CharField(source="stock__barcode__barcode_no")
    material_name = serializers.CharField(source="stock__product__name")
    ucs_code = serializers.CharField(source="stock__product__ucs_code")
    stock_out_date = serializers.DateField(source="created_at__date", format="%d %b %Y")

    class Meta:
        fields = ("material_name", "ucs_code", "barcode", "actual_barcode", "stock_out_date")


class ReportDeadStockItemSerializer(serializers.Serializer):
    material_name = serializers.CharField(source="name")
    ucs_code = serializers.CharField()
    net_quantity = serializers.IntegerField()

    class Meta:
        fields = ("material_name", "ucs_code", "net_quantity")
