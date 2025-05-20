import os
from django.conf import settings
from rest_framework import serializers
from .models import Users


class CustomerLoginDataDataSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(CustomerLoginDataDataSerializer, self).to_representation(obj)
        ret["designation"] = (
            {"id": obj.designation.id, "name": obj.designation.name}
            if obj.designation
            else None
        )
        ret["status"] = "Active" if obj.is_active else "Inactive"
        return ret

    class Meta:
        model = Users
        fields = [
            "name",
            "email",
            "personnel_number",
            "date_joined",
            "last_login",
            "role",
            "mobile_number",
            "user_permission",
        ]
        read_only_fields = fields
