import os
from django.conf import settings
from rest_framework import serializers
from .models import User


class CustomerLoginDataDataSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(CustomerLoginDataDataSerializer, self).to_representation(obj)
        ret["status"] = "Active" if obj.is_active else "Inactive"
        return ret

    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "last_login",
            "role",
            "personnel_number",
            "area",
        ]
        read_only_fields = fields
