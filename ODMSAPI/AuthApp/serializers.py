from rest_framework import serializers
from .models import User

class UserProfileSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(UserProfileSerializer, self).to_representation(obj)
        ret['status'] = "Active" if obj.is_active else "Inactive"
        ret['department'] = {
                "id":obj.department.id,
                "name":obj.department.name, 
                "department_id":obj.department.department_id
            } if obj.department else None
        return ret
    class Meta:
        model = User
        fields = ["id", "full_name", "profile_photo", "email", "personnel_number", "phone_number", "last_login", "role", "designation", "drawing_permission", "standard_permission", "document_permission"]
        read_only_fields = fields
