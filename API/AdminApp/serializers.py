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
    Source
)
from AuthApp.models import Users, Designation


class RacksSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(RacksSerializer, self).to_representation(obj)
        ret["product"] = obj.product if hasattr(obj, "product") else 0
        ret["barcode_no"] = obj.barcode.barcode_no
        ret["most_stock_product"] = (
            obj.most_product_name if hasattr(obj, "most_product_name") else None
        )
        ret["most_stock_product_quantity"] = (
            obj.most_product_qunatity if hasattr(obj, "most_product_qunatity") else 0
        )
        return ret

    class Meta:
        model = Racks
        fields = ["id", "rack_no"]
        read_only_fields = fields


class RacksProductDetailsSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(RacksProductDetailsSerializer, self).to_representation(obj)
        rack_id = self.context.get("rack_id")
        ret["stocks"] = (
            Stocks.objects.select_related("product", "rack")
            .filter(product=obj, rack__id=rack_id)
            .values("barcode__barcode_no", "quantity", "source", "created_at")
        )
        return ret

    class Meta:
        model = Products
        fields = ["id", "name", "ucs_code", "net_quantity"]
        read_only_fields = fields


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
        ret["label"] = f"{obj.name} ({obj.personnel_number})"
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
        fields = ["id", "quantity", "source"]
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
        ret["source"] = obj.source.name
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
            "source": obj.stock.source.name,
            "barcode_no": obj.stock.barcode.barcode_no,
        }
        ret["created_at"] = obj.created_at.strftime("%d %b %Y, %I:%M %p")
        return ret

    class Meta:
        model = StocksHistory
        fields = ["id", "quantity", "is_stock_out", "product_quantity", "purpose", "history_type"]
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
