from rest_framework import serializers
from .models import User

class UserProfileSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(UserProfileSerializer, self).to_representation(obj)
        ret['status'] = "Active" if obj.is_active else "Inactive"
        return ret
    class Meta:
        model = User
        fields = ["name", "personnel_number", "last_login", "role"]
        read_only_fields = fields
