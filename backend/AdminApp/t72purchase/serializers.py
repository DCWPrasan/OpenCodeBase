from rest_framework import serializers
from AdminApp.models import (
    T72Purchase,
    T72PurchaseItem,
    T72Status,
    T72ItemIssuedHistory,
)
from datetime import date
from AuthApp.models import Users


class T72ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = T72PurchaseItem
        fields = [
            "id",
            "item_name",
            "quantity",
            "available_quantity",
            "unit",
            "location",
        ]
        read_only_fields = ["available_quantity"]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Convert decimal/float to int for display
        if ret.get("quantity") is not None:
            ret["quantity"] = int(float(ret["quantity"]))
        if ret.get("available_quantity") is not None:
            ret["available_quantity"] = int(float(ret["available_quantity"]))
        return ret


class T72CreateUpdateSerializer(serializers.ModelSerializer):
    items = T72ItemSerializer(many=True)

    class Meta:
        model = T72Purchase
        exclude = ["created_by", "status"]
        extra_kwargs = {
            "order_number": {
                "error_messages": {"unique": "This Order Number already exists."}
            },
            "challan_number": {
                "error_messages": {"unique": "This Challan Number already exists."}
            },
            "daybook_number": {
                "error_messages": {"unique": "This Daybook Number already exists."}
            },
        }

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["status"] = instance.status
        if instance.authorized_by:
            response["authorized_by"] = SearchUserSerializer(
                instance.authorized_by
            ).data
        if instance.created_by:
            response["created_by"] = SearchUserSerializer(instance.created_by).data
        return response

    def validate_receive_date(self, value):
        if value > date.today():
            raise serializers.ValidationError("Future receive date not allowed")
        return value

    def validate_items(self, items):
        names = [i["item_name"] for i in items]
        if len(names) != len(set(names)):
            raise serializers.ValidationError("Duplicate item not allowed")
        return items

    def create(self, validated_data):
        items = validated_data.pop("items")
        # Status defaults to RECEIVED
        purchase = T72Purchase.objects.create(
            created_by=self.context["request"].user, **validated_data
        )
        for item in items:
            # Init available_quantity same as quantity
            T72PurchaseItem.objects.create(
                purchase=purchase, available_quantity=item["quantity"], **item
            )
        return purchase

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)

        if instance.issued_history.exists():
            # If any item has been issued, prevent updating items to ensure integrity
            if items_data is not None:
                raise serializers.ValidationError(
                    "Cannot update items after an issuance has occurred."
                )

        # Update main instance fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update nested items
        if items_data is not None:
            # Clear existing items and recreate
            instance.items.all().delete()
            for item in items_data:
                T72PurchaseItem.objects.create(
                    purchase=instance, available_quantity=item["quantity"], **item
                )

        return instance


class T72ListSerializer(serializers.ModelSerializer):
    item_names = serializers.SerializerMethodField()

    class Meta:
        model = T72Purchase
        fields = [
            "id",
            "receive_date",
            "party_name",
            "order_number",
            "challan_number",
            "daybook_number",
            "used_area",
            "remarks",
            "status",
            "item_names",
            "created_at",
        ]

    def get_item_names(self, obj):
        return ", ".join([item.item_name for item in obj.items.all()])


class SearchUserSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(SearchUserSerializer, self).to_representation(obj)
        ret["label"] = (
            f"{obj.name} ({obj.personnel_number})" if obj.personnel_number else obj.name
        )
        ret["value"] = obj.id
        return ret

    class Meta:
        model = Users
        fields = []


class T72ItemIssuedHistorySerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.item_name", read_only=True)
    unit = serializers.CharField(source="item.unit", read_only=True)
    order_number = serializers.CharField(source="purchase.order_number", read_only=True)
    issued_by_name = serializers.CharField(source="issue_by.name", read_only=True)
    received_by_name = serializers.CharField(source="received_by.name", read_only=True)

    class Meta:
        model = T72ItemIssuedHistory
        fields = [
            "id",
            "purchase",
            "order_number",
            "item",
            "item_name",
            "unit",
            "quantity",
            "issue_at",
            "issue_by",
            "issued_by_name",
            "received_by",
            "received_by_name",
        ]
